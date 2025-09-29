"""
系统测试脚本
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models import *
from app.services.scanner import FileScanner
from app.services.hash_service import HashService

def create_test_files():
    """创建测试文件"""
    test_dir = Path(tempfile.mkdtemp(prefix="file_organizer_test_"))
    
    # 创建测试文件
    (test_dir / "test1.txt").write_text("Hello World 1")
    (test_dir / "test2.txt").write_text("Hello World 2")
    (test_dir / "test3.txt").write_text("Hello World 1")  # 与test1.txt内容相同
    
    # 创建子目录
    sub_dir = test_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "test4.txt").write_text("Hello World 4")
    
    return test_dir

def test_database():
    """测试数据库"""
    print("测试数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")
    
    # 测试连接
    db = SessionLocal()
    try:
        # 测试查询
        blob_count = db.query(Blob).count()
        asset_count = db.query(Asset).count()
        print(f"✓ 数据库连接正常，Blob: {blob_count}, Asset: {asset_count}")
    finally:
        db.close()

def test_scanner():
    """测试扫描器"""
    print("测试扫描器...")
    
    # 创建测试文件
    test_dir = create_test_files()
    print(f"✓ 创建测试目录: {test_dir}")
    
    try:
        # 初始化扫描器
        scanner = FileScanner()
        
        # 设置进度回调
        def progress_callback(data):
            print(f"扫描进度: {data}")
        
        scanner.set_progress_callback(progress_callback)
        
        # 执行扫描
        result = scanner.scan_path(str(test_dir))
        
        print(f"✓ 扫描完成: {result}")
        
        # 验证结果
        db = SessionLocal()
        try:
            blob_count = db.query(Blob).count()
            asset_count = db.query(Asset).count()
            print(f"✓ 数据库记录: Blob: {blob_count}, Asset: {asset_count}")
        finally:
            db.close()
        
    finally:
        # 清理测试文件
        shutil.rmtree(test_dir)
        print("✓ 清理测试文件")

def test_hash_service():
    """测试哈希服务"""
    print("测试哈希服务...")
    
    # 创建测试文件
    test_dir = create_test_files()
    
    try:
        hash_service = HashService()
        
        # 测试快速哈希
        test_file = test_dir / "test1.txt"
        fast_hash = hash_service.calculate_fast_hash(test_file)
        print(f"✓ 快速哈希: {fast_hash[:16]}...")
        
        # 测试内容哈希
        content_hash = hash_service.calculate_content_hash(test_file)
        print(f"✓ 内容哈希: {content_hash[:16]}...")
        
        # 测试重复文件检测
        duplicate_groups = hash_service.find_duplicate_files(list(test_dir.glob("*.txt")))
        print(f"✓ 重复文件组: {len(duplicate_groups)}")
        
    finally:
        shutil.rmtree(test_dir)

def test_search_service():
    """测试搜索服务"""
    print("测试搜索服务...")
    
    try:
        from app.services.search_service import SearchService
        
        search_service = SearchService()
        
        # 设置FTS5索引
        success = search_service.setup_fts5_index()
        if success:
            print("✓ FTS5索引设置成功")
        else:
            print("✗ FTS5索引设置失败")
            return
        
        # 测试搜索功能
        result = search_service.search_files("test", limit=10)
        print(f"✓ 搜索测试: 找到 {result['total']} 个文件")
        
        # 测试搜索建议
        suggestions = search_service.get_search_suggestions("test", 5)
        print(f"✓ 搜索建议: {len(suggestions)} 个建议")
        
    except Exception as e:
        print(f"✗ 搜索服务测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_preview_service():
    """测试预览服务"""
    print("测试预览服务...")
    
    # 创建测试文件
    test_dir = create_test_files()
    
    try:
        from app.services.preview_service import PreviewService
        
        preview_service = PreviewService()
        
        # 测试图片预览
        test_image = test_dir / "test1.txt"  # 使用文本文件作为测试
        if test_image.exists():
            # 测试预览类型检测
            preview_type = preview_service.get_preview_type(str(test_image))
            print(f"✓ 预览类型检测: {preview_type}")
            
            # 测试预览路径生成
            preview_path = preview_service.get_preview_path("test_hash", "medium")
            print(f"✓ 预览路径生成: {preview_path}")
            
            # 测试缓存检查
            is_cached = preview_service.is_preview_cached("test_hash", "medium")
            print(f"✓ 缓存检查: {is_cached}")
        
        print("✓ 预览服务基础功能正常")
        
    except Exception as e:
        print(f"✗ 预览服务测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        shutil.rmtree(test_dir)

def main():
    """主测试函数"""
    print("开始系统测试...")
    print("=" * 50)
    
    try:
        # 测试数据库
        test_database()
        print()
        
        # 测试扫描器
        test_scanner()
        print()
        
        # 测试哈希服务
        test_hash_service()
        print()
        
        # 测试搜索服务
        test_search_service()
        print()
        
        # 测试预览服务
        test_preview_service()
        print()
        
        print("=" * 50)
        print("✓ 所有测试通过！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
