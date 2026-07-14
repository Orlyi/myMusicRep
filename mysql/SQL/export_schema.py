"""
数据库结构导出脚本
运行后自动在脚本所在目录生成 create.sql 文件
如果有则覆盖
"""

import os
import subprocess
import sys

def get_mysql_connection_config():
    """
    获取 MySQL 连接配置
    在这里修改你的数据库连接信息
    """
    return {
        'host': 'localhost',
        'user': 'root',
        'password': 'sql2008',  # ⚠️ 改成你的 MySQL 密码
        'database': 'mymusic',
        'port': '3306'
    }

def get_mysqldump_path():
    """
    获取 mysqldump 的完整路径
    根据你的 MySQL 安装位置修改
    """
    # ⚠️ 改成你实际的 MySQL 安装路径
    # 最常见的是这个：
    return r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

    # 如果上面不对，试试下面这些（取消注释）：
    # return r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump"
    # return r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
    # return r"C:\xampp\mysql\bin\mysqldump.exe"

def export_schema():
    """导出数据库结构到 create.sql"""

    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, 'create.sql')

    # 获取配置
    config = get_mysql_connection_config()
    mysqldump_path = get_mysqldump_path()

    # 检查 mysqldump 是否存在
    if not os.path.exists(mysqldump_path):
        print(f"❌ 找不到 mysqldump: {mysqldump_path}")
        print("   请检查 get_mysqldump_path() 函数中的路径是否正确")
        return False

    # 构建命令
    cmd = [
        mysqldump_path,
        f'-h{config["host"]}',
        f'-P{config["port"]}',
        f'-u{config["user"]}',
        f'-p{config["password"]}',
        '--no-data',
        '--routines',
        '--triggers',
        '--add-drop-table',
        '--default-character-set=utf8mb4',
        config['database'],
    ]

    try:
        print(f"正在导出数据库结构: {config['database']}...")
        print(f"使用 mysqldump: {mysqldump_path}")

        # 执行命令并捕获输出
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            print(f"❌ 导出失败: {result.stderr}")
            return False

        # 写入文件（覆盖）
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)

        print(f"✅ 导出成功: {output_file}")

        # 显示文件大小
        file_size = os.path.getsize(output_file)
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{file_size / 1024:.2f} KB"
        print(f"📄 文件大小: {size_str}")

        return True

    except Exception as e:
        print(f"❌ 导出失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("MySQL 数据库结构导出工具")
    print("=" * 50)

    success = export_schema()

    if success:
        print("\n✅ 完成！按任意键退出...")
    else:
        print("\n❌ 失败！请检查配置后重试")
        print("按任意键退出...")

    input()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()