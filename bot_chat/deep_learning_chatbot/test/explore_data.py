import pandas as pd

# Đọc dữ liệu
df = pd.read_csv('healthcare_dataset.csv')

# Hiển thị thông tin cơ bản
print("=== THÔNG TIN CƠ BẢN VỀ DATASET ===")
print(f"Kích thước dataset: {df.shape}")
print(f"Các cột: {list(df.columns)}")
print("\n=== VÀI DÒNG ĐẦU TIÊN ===")
print(df.head())

print("\n=== THÔNG TIN CHI TIẾT ===")
print(df.info())

print("\n=== THỐNG KÊ MÔ TẢ ===")
print(df.describe())

# Kiểm tra giá trị null
print("\n=== GIÁ TRỊ NULL ===")
print(df.isnull().sum()) 