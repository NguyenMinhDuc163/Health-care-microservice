import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

class SimpleHealthcareChatbot:
    def __init__(self):
        self.condition_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.medication_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.condition_encoder = LabelEncoder()
        self.medication_encoder = LabelEncoder()
        self.feature_columns = ['Age', 'Gender', 'Blood Type', 'Admission Type', 'Test Results']
        
    def load_and_preprocess_data(self, file_path, sample_size=1000):
        """Tải và xử lý dữ liệu từ CSV file"""
        print("🔄 Đang tải dữ liệu...")
        
        # Đọc dữ liệu - chỉ lấy sample_size dòng đầu để test
        df = pd.read_csv(file_path, nrows=sample_size)
        print(f"📊 Đã tải {len(df)} bản ghi")
        
        # Làm sạch dữ liệu
        df = df.dropna()
        print(f"📊 Sau khi loại bỏ dữ liệu thiếu: {len(df)} bản ghi")
        
        # Chuẩn hóa tên cột
        df.columns = df.columns.str.strip()
        
        return df
    
    def encode_features(self, df):
        """Mã hóa các đặc trưng categorical"""
        print("🔄 Đang mã hóa dữ liệu...")
        
        df_encoded = df.copy()
        
        # Mã hóa các cột categorical
        categorical_columns = ['Gender', 'Blood Type', 'Admission Type', 'Test Results']
        
        for col in categorical_columns:
            if col in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self.label_encoders[col] = le
        
        # Chuẩn hóa tuổi
        df_encoded['Age'] = self.scaler.fit_transform(df_encoded[['Age']])
        
        return df_encoded
    
    def prepare_training_data(self, df_encoded):
        """Chuẩn bị dữ liệu training"""
        # Features (X)
        X = df_encoded[self.feature_columns].values
        
        # Targets (y)
        y_condition = self.condition_encoder.fit_transform(df_encoded['Medical Condition'])
        y_medication = self.medication_encoder.fit_transform(df_encoded['Medication'])
        
        return X, y_condition, y_medication
    
    def train_models(self, X, y_condition, y_medication):
        """Training các models"""
        print("🚀 Bắt đầu training models...")
        
        # Chia dữ liệu train/test
        X_train, X_test, y_cond_train, y_cond_test, y_med_train, y_med_test = train_test_split(
            X, y_condition, y_medication, test_size=0.2, random_state=42
        )
        
        # Training model cho Medical Condition
        print("🔄 Training model dự đoán tình trạng bệnh...")
        self.condition_model.fit(X_train, y_cond_train)
        
        # Training model cho Medication
        print("🔄 Training model đề xuất thuốc...")
        self.medication_model.fit(X_train, y_med_train)
        
        # Đánh giá models
        print("\n📊 Đánh giá hiệu quả models:")
        
        # Condition model
        cond_pred = self.condition_model.predict(X_test)
        cond_accuracy = accuracy_score(y_cond_test, cond_pred)
        print(f"🎯 Độ chính xác dự đoán tình trạng bệnh: {cond_accuracy:.3f}")
        
        # Medication model  
        med_pred = self.medication_model.predict(X_test)
        med_accuracy = accuracy_score(y_med_test, med_pred)
        print(f"💊 Độ chính xác đề xuất thuốc: {med_accuracy:.3f}")
        
        return cond_accuracy, med_accuracy
    
    def save_models(self):
        """Lưu models và encoders"""
        print("💾 Đang lưu models...")
        
        with open('simple_models.pkl', 'wb') as f:
            pickle.dump({
                'condition_model': self.condition_model,
                'medication_model': self.medication_model,
                'label_encoders': self.label_encoders,
                'scaler': self.scaler,
                'condition_encoder': self.condition_encoder,
                'medication_encoder': self.medication_encoder
            }, f)
        
        print("✅ Đã lưu models thành công!")
    
    def load_models(self):
        """Tải models đã lưu"""
        try:
            with open('simple_models.pkl', 'rb') as f:
                data = pickle.load(f)
                self.condition_model = data['condition_model']
                self.medication_model = data['medication_model']
                self.label_encoders = data['label_encoders']
                self.scaler = data['scaler']
                self.condition_encoder = data['condition_encoder']
                self.medication_encoder = data['medication_encoder']
            
            print("✅ Đã tải models thành công!")
            return True
        except:
            print("❌ Không thể tải models. Cần training lại.")
            return False
    
    def predict(self, age, gender, blood_type, admission_type, test_results):
        """Dự đoán cho bệnh nhân mới"""
        try:
            # Chuẩn bị input
            input_data = {
                'Age': [age],
                'Gender': [gender],
                'Blood Type': [blood_type], 
                'Admission Type': [admission_type],
                'Test Results': [test_results]
            }
            
            df_input = pd.DataFrame(input_data)
            
            # Encode input
            for col in ['Gender', 'Blood Type', 'Admission Type', 'Test Results']:
                if col in self.label_encoders:
                    try:
                        df_input[col] = self.label_encoders[col].transform(df_input[col])
                    except:
                        # Nếu giá trị mới không có trong training data
                        df_input[col] = 0
            
            df_input['Age'] = self.scaler.transform(df_input[['Age']])
            
            X_input = df_input[self.feature_columns].values
            
            # Dự đoán
            condition_pred = self.condition_model.predict(X_input)[0]
            medication_pred = self.medication_model.predict(X_input)[0]
            
            # Lấy probability để đánh giá confidence
            condition_proba = np.max(self.condition_model.predict_proba(X_input)[0])
            medication_proba = np.max(self.medication_model.predict_proba(X_input)[0])
            
            # Chuyển đổi về tên gốc
            predicted_condition = self.condition_encoder.inverse_transform([condition_pred])[0]
            predicted_medication = self.medication_encoder.inverse_transform([medication_pred])[0]
            
            return {
                'condition': predicted_condition,
                'condition_confidence': condition_proba,
                'medication': predicted_medication,
                'medication_confidence': medication_proba
            }
            
        except Exception as e:
            return f"❌ Lỗi dự đoán: {str(e)}"
    
    def get_sample_predictions(self):
        """Hiển thị một số dự đoán mẫu"""
        print("\n🎯 CÁC DỰ ĐOÁN MẪU:")
        print("=" * 50)
        
        samples = [
            (45, "Male", "A+", "Emergency", "Abnormal"),
            (60, "Female", "O-", "Urgent", "Normal"),
            (25, "Male", "B+", "Elective", "Inconclusive"),
            (70, "Female", "AB+", "Emergency", "Abnormal")
        ]
        
        for i, (age, gender, blood, admission, test) in enumerate(samples, 1):
            print(f"\n📋 Mẫu {i}: Tuổi {age}, {gender}, {blood}, {admission}, {test}")
            result = self.predict(age, gender, blood, admission, test)
            if isinstance(result, dict):
                print(f"   🏥 Dự đoán: {result['condition']} (tin cậy: {result['condition_confidence']:.2%})")
                print(f"   💊 Thuốc: {result['medication']} (tin cậy: {result['medication_confidence']:.2%})")
            else:
                print(f"   ❌ {result}")
    
    def chat(self):
        """Interface chat với người dùng"""
        print("\n🤖 SIMPLE HEALTHCARE CHATBOT")
        print("=" * 50)
        print("Xin chào! Tôi là chatbot y tế đơn giản. Tôi có thể giúp dự đoán tình trạng bệnh và đề xuất thuốc.")
        print("Nhập 'quit' để thoát, 'sample' để xem dự đoán mẫu.\n")
        
        while True:
            choice = input("\n📝 Nhập 'predict' để dự đoán mới, 'sample' để xem mẫu, hoặc 'quit' để thoát: ").lower()
            
            if choice == 'quit':
                break
            elif choice == 'sample':
                self.get_sample_predictions()
                continue
            elif choice != 'predict':
                print("❌ Vui lòng nhập 'predict', 'sample' hoặc 'quit'")
                continue
            
            print("\n📝 Vui lòng nhập thông tin bệnh nhân:")
            
            try:
                age = input("Tuổi: ")
                if age.lower() == 'quit':
                    break
                age = int(age)
                
                gender = input("Giới tính (Male/Female): ")
                if gender.lower() == 'quit':
                    break
                
                blood_type = input("Nhóm máu (A+, A-, B+, B-, AB+, AB-, O+, O-): ")
                if blood_type.lower() == 'quit':
                    break
                
                admission_type = input("Loại nhập viện (Emergency/Urgent/Elective): ")
                if admission_type.lower() == 'quit':
                    break
                
                test_results = input("Kết quả xét nghiệm (Normal/Abnormal/Inconclusive): ")
                if test_results.lower() == 'quit':
                    break
                
                # Dự đoán
                result = self.predict(age, gender, blood_type, admission_type, test_results)
                
                if isinstance(result, dict):
                    print(f"\n🔍 KẾT QUẢ DỰ ĐOÁN:")
                    print(f"🏥 Tình trạng bệnh dự đoán: {result['condition']}")
                    print(f"📊 Độ tin cậy: {result['condition_confidence']:.2%}")
                    print(f"💊 Thuốc đề xuất: {result['medication']}")
                    print(f"📊 Độ tin cậy: {result['medication_confidence']:.2%}")
                    print("\n⚠️  LƯU Ý: Kết quả chỉ mang tính chất tham khảo. Vui lòng tham khảo ý kiến bác sĩ!")
                else:
                    print(result)
                    
            except KeyboardInterrupt:
                break
            except ValueError:
                print("❌ Vui lòng nhập đúng định dạng!")
            except Exception as e:
                print(f"❌ Lỗi: {str(e)}")
        
        print("\n👋 Cảm ơn bạn đã sử dụng Healthcare Chatbot!")

def main():
    """Hàm main để chạy chatbot"""
    chatbot = SimpleHealthcareChatbot()
    
    # Kiểm tra xem đã có models trained chưa
    if not chatbot.load_models():
        print("🔄 Bắt đầu training models...")
        
        # Tải và xử lý dữ liệu (chỉ lấy 1000 samples để test nhanh)
        df = chatbot.load_and_preprocess_data('healthcare_dataset.csv', sample_size=1000)
        df_encoded = chatbot.encode_features(df)
        X, y_condition, y_medication = chatbot.prepare_training_data(df_encoded)
        
        # Training models
        chatbot.train_models(X, y_condition, y_medication)
        
        # Lưu models
        chatbot.save_models()
    
    # Hiển thị thông tin
    print("\n✅ CHATBOT SẴN SÀNG!")
    print("📋 Model này sử dụng Random Forest để dự đoán:")
    print("   - Tình trạng bệnh dựa trên thông tin bệnh nhân")
    print("   - Thuốc phù hợp cho từng trường hợp")
    
    # Bắt đầu chat
    chatbot.chat()

if __name__ == "__main__":
    main() 