"""
相似度算法服务
"""
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from PIL import Image
import logging
from app.database import SessionLocal
from app.models import Blob, Asset
from app.services.hash_service import HashService

logger = logging.getLogger(__name__)

class SimilarityService:
    """相似度算法服务"""
    
    def __init__(self):
        self.hash_service = HashService()
        
        # 相似度阈值配置
        self.similarity_thresholds = {
            'image': 0.8,      # 图片相似度阈值
            'audio': 0.7,      # 音频相似度阈值
            'document': 0.6,   # 文档相似度阈值
            'video': 0.8       # 视频相似度阈值
        }
    
    def calculate_image_phash(self, image_path: str) -> Optional[str]:
        """计算图片感知哈希"""
        try:
            from PIL import Image
            import imagehash
            
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算感知哈希
                phash = imagehash.phash(img)
                return str(phash)
                
        except Exception as e:
            logger.error(f"计算图片感知哈希失败: {image_path}, 错误: {e}")
            return None
    
    def calculate_audio_fingerprint(self, audio_path: str) -> Optional[str]:
        """计算音频指纹"""
        try:
            import librosa
            import numpy as np
            
            # 加载音频文件
            y, sr = librosa.load(audio_path, sr=22050)
            
            # 计算MFCC特征
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 计算特征向量的均值作为指纹
            fingerprint = np.mean(mfccs, axis=1)
            
            # 转换为字符串
            fingerprint_str = ','.join([f"{x:.6f}" for x in fingerprint])
            
            return fingerprint_str
            
        except Exception as e:
            logger.error(f"计算音频指纹失败: {audio_path}, 错误: {e}")
            return None
    
    def calculate_document_similarity(self, doc1_path: str, doc2_path: str) -> float:
        """计算文档相似度"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            # 读取文档内容
            content1 = self.extract_text_content(doc1_path)
            content2 = self.extract_text_content(doc2_path)
            
            if not content1 or not content2:
                return 0.0
            
            # 使用TF-IDF向量化
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([content1, content2])
            
            # 计算余弦相似度
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"计算文档相似度失败: {doc1_path}, {doc2_path}, 错误: {e}")
            return 0.0
    
    def extract_text_content(self, file_path: str) -> str:
        """提取文档文本内容"""
        try:
            ext = Path(file_path).suffix.lower()
            
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif ext == '.pdf':
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text
            
            elif ext in ['.doc', '.docx']:
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            
            else:
                return ""
                
        except Exception as e:
            logger.error(f"提取文档内容失败: {file_path}, 错误: {e}")
            return ""
    
    def calculate_image_similarity(self, phash1: str, phash2: str) -> float:
        """计算图片相似度"""
        try:
            import imagehash
            
            # 将字符串转换为哈希对象
            hash1 = imagehash.hex_to_hash(phash1)
            hash2 = imagehash.hex_to_hash(phash2)
            
            # 计算汉明距离
            hamming_distance = hash1 - hash2
            
            # 转换为相似度 (0-1)
            max_distance = 64  # 感知哈希的最大汉明距离
            similarity = 1.0 - (hamming_distance / max_distance)
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"计算图片相似度失败: {phash1}, {phash2}, 错误: {e}")
            return 0.0
    
    def calculate_audio_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """计算音频相似度"""
        try:
            # 解析指纹字符串
            fp1 = [float(x) for x in fingerprint1.split(',')]
            fp2 = [float(x) for x in fingerprint2.split(',')]
            
            if len(fp1) != len(fp2):
                return 0.0
            
            # 计算欧几里得距离
            distance = np.linalg.norm(np.array(fp1) - np.array(fp2))
            
            # 转换为相似度 (0-1)
            similarity = 1.0 / (1.0 + distance)
            
            return similarity
            
        except Exception as e:
            logger.error(f"计算音频相似度失败: {fingerprint1}, {fingerprint2}, 错误: {e}")
            return 0.0
    
    def find_similar_files(self, content_hash: str, file_type: str = None, threshold: float = None) -> List[Dict[str, Any]]:
        """查找相似文件"""
        try:
            db = SessionLocal()
            
            # 获取源文件信息
            source_blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
            if not source_blob:
                return []
            
            # 设置阈值
            if threshold is None:
                threshold = self.similarity_thresholds.get(file_type, 0.8)
            
            similar_files = []
            
            # 根据文件类型查找相似文件
            if file_type == 'image' and source_blob.phash:
                similar_files = self.find_similar_images(db, source_blob.phash, threshold)
            elif file_type == 'audio' and source_blob.audio_fingerprint:
                similar_files = self.find_similar_audio(db, source_blob.audio_fingerprint, threshold)
            elif file_type == 'document':
                similar_files = self.find_similar_documents(db, content_hash, threshold)
            else:
                # 通用相似度查找
                similar_files = self.find_similar_general(db, content_hash, threshold)
            
            db.close()
            return similar_files
            
        except Exception as e:
            logger.error(f"查找相似文件失败: {content_hash}, 错误: {e}")
            return []
    
    def find_similar_images(self, db, source_phash: str, threshold: float) -> List[Dict[str, Any]]:
        """查找相似图片"""
        try:
            similar_files = []
            
            # 获取所有有感知哈希的图片
            blobs = db.query(Blob).filter(
                Blob.phash.isnot(None),
                Blob.primary_type == 'image'
            ).all()
            
            for blob in blobs:
                if blob.phash and blob.phash != source_phash:
                    similarity = self.calculate_image_similarity(source_phash, blob.phash)
                    
                    if similarity >= threshold:
                        # 获取文件路径
                        asset = db.query(Asset).filter(
                            Asset.content_hash == blob.content_hash,
                            Asset.is_available == True
                        ).first()
                        
                        if asset:
                            similar_files.append({
                                'content_hash': blob.content_hash,
                                'file_path': asset.full_path,
                                'similarity': similarity,
                                'file_type': 'image',
                                'size': blob.size
                            })
            
            # 按相似度排序
            similar_files.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_files
            
        except Exception as e:
            logger.error(f"查找相似图片失败: {e}")
            return []
    
    def find_similar_audio(self, db, source_fingerprint: str, threshold: float) -> List[Dict[str, Any]]:
        """查找相似音频"""
        try:
            similar_files = []
            
            # 获取所有有音频指纹的音频文件
            blobs = db.query(Blob).filter(
                Blob.audio_fingerprint.isnot(None),
                Blob.primary_type == 'audio'
            ).all()
            
            for blob in blobs:
                if blob.audio_fingerprint and blob.audio_fingerprint != source_fingerprint:
                    similarity = self.calculate_audio_similarity(source_fingerprint, blob.audio_fingerprint)
                    
                    if similarity >= threshold:
                        # 获取文件路径
                        asset = db.query(Asset).filter(
                            Asset.content_hash == blob.content_hash,
                            Asset.is_available == True
                        ).first()
                        
                        if asset:
                            similar_files.append({
                                'content_hash': blob.content_hash,
                                'file_path': asset.full_path,
                                'similarity': similarity,
                                'file_type': 'audio',
                                'size': blob.size
                            })
            
            # 按相似度排序
            similar_files.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_files
            
        except Exception as e:
            logger.error(f"查找相似音频失败: {e}")
            return []
    
    def find_similar_documents(self, db, source_content_hash: str, threshold: float) -> List[Dict[str, Any]]:
        """查找相似文档"""
        try:
            similar_files = []
            
            # 获取源文档路径
            source_asset = db.query(Asset).filter(
                Asset.content_hash == source_content_hash,
                Asset.is_available == True
            ).first()
            
            if not source_asset:
                return []
            
            # 获取所有文档文件
            blobs = db.query(Blob).filter(
                Blob.primary_type == 'document'
            ).all()
            
            for blob in blobs:
                if blob.content_hash != source_content_hash:
                    # 获取文件路径
                    asset = db.query(Asset).filter(
                        Asset.content_hash == blob.content_hash,
                        Asset.is_available == True
                    ).first()
                    
                    if asset:
                        # 计算文档相似度
                        similarity = self.calculate_document_similarity(
                            source_asset.full_path,
                            asset.full_path
                        )
                        
                        if similarity >= threshold:
                            similar_files.append({
                                'content_hash': blob.content_hash,
                                'file_path': asset.full_path,
                                'similarity': similarity,
                                'file_type': 'document',
                                'size': blob.size
                            })
            
            # 按相似度排序
            similar_files.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_files
            
        except Exception as e:
            logger.error(f"查找相似文档失败: {e}")
            return []
    
    def find_similar_general(self, db, source_content_hash: str, threshold: float) -> List[Dict[str, Any]]:
        """通用相似度查找"""
        try:
            similar_files = []
            
            # 获取源文件信息
            source_blob = db.query(Blob).filter(Blob.content_hash == source_content_hash).first()
            if not source_blob:
                return []
            
            # 获取所有文件
            blobs = db.query(Blob).filter(Blob.content_hash != source_content_hash).all()
            
            for blob in blobs:
                similarity = 0.0
                
                # 根据文件类型计算相似度
                if blob.primary_type == 'image' and source_blob.primary_type == 'image':
                    if blob.phash and source_blob.phash:
                        similarity = self.calculate_image_similarity(source_blob.phash, blob.phash)
                
                elif blob.primary_type == 'audio' and source_blob.primary_type == 'audio':
                    if blob.audio_fingerprint and source_blob.audio_fingerprint:
                        similarity = self.calculate_audio_similarity(source_blob.audio_fingerprint, blob.audio_fingerprint)
                
                elif blob.primary_type == 'document' and source_blob.primary_type == 'document':
                    # 获取文件路径计算文档相似度
                    source_asset = db.query(Asset).filter(
                        Asset.content_hash == source_content_hash,
                        Asset.is_available == True
                    ).first()
                    asset = db.query(Asset).filter(
                        Asset.content_hash == blob.content_hash,
                        Asset.is_available == True
                    ).first()
                    
                    if source_asset and asset:
                        similarity = self.calculate_document_similarity(
                            source_asset.full_path,
                            asset.full_path
                        )
                
                if similarity >= threshold:
                    # 获取文件路径
                    asset = db.query(Asset).filter(
                        Asset.content_hash == blob.content_hash,
                        Asset.is_available == True
                    ).first()
                    
                    if asset:
                        similar_files.append({
                            'content_hash': blob.content_hash,
                            'file_path': asset.full_path,
                            'similarity': similarity,
                            'file_type': blob.primary_type,
                            'size': blob.size
                        })
            
            # 按相似度排序
            similar_files.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_files
            
        except Exception as e:
            logger.error(f"通用相似度查找失败: {e}")
            return []
    
    def group_similar_files(self, file_type: str = None, threshold: float = None) -> List[List[Dict[str, Any]]]:
        """分组相似文件"""
        try:
            db = SessionLocal()
            
            # 设置阈值
            if threshold is None:
                threshold = self.similarity_thresholds.get(file_type, 0.8)
            
            # 获取所有文件
            query = db.query(Blob)
            if file_type:
                query = query.filter(Blob.primary_type == file_type)
            
            blobs = query.all()
            
            # 分组相似文件
            groups = []
            processed = set()
            
            for blob in blobs:
                if blob.content_hash in processed:
                    continue
                
                # 查找相似文件
                similar_files = self.find_similar_files(blob.content_hash, file_type, threshold)
                
                if similar_files:
                    # 创建组
                    group = [{
                        'content_hash': blob.content_hash,
                        'file_type': blob.primary_type,
                        'size': blob.size
                    }]
                    
                    for similar in similar_files:
                        group.append(similar)
                        processed.add(similar['content_hash'])
                    
                    groups.append(group)
                
                processed.add(blob.content_hash)
            
            db.close()
            return groups
            
        except Exception as e:
            logger.error(f"分组相似文件失败: {e}")
            return []
    
    def update_file_similarity(self, content_hash: str, file_path: str) -> bool:
        """更新文件相似度信息"""
        try:
            db = SessionLocal()
            
            # 获取文件信息
            blob = db.query(Blob).filter(Blob.content_hash == content_hash).first()
            if not blob:
                return False
            
            # 根据文件类型更新相似度信息
            if blob.primary_type == 'image':
                phash = self.calculate_image_phash(file_path)
                if phash:
                    blob.phash = phash
            
            elif blob.primary_type == 'audio':
                fingerprint = self.calculate_audio_fingerprint(file_path)
                if fingerprint:
                    blob.audio_fingerprint = fingerprint
            
            db.commit()
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"更新文件相似度信息失败: {content_hash}, 错误: {e}")
            return False
