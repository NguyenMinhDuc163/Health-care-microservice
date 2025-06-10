import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

# Cấu hình trang
st.set_page_config(
    page_title="🏥 Healthcare Chatbot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS để tùy chỉnh giao diện
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        background-color: #f1f8e9;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        background-color: #fff3e0;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #f44336;
        background-color: #ffebee;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        background-color: #e3f2fd;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitHealthcareChatbot:
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
        try:
            df = pd.read_csv(file_path, nrows=sample_size)
            df = df.dropna()
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu: {str(e)}")
            return None
    
    def encode_features(self, df):
        """Mã hóa các đặc trưng categorical"""
        df_encoded = df.copy()
        categorical_columns = ['Gender', 'Blood Type', 'Admission Type', 'Test Results']
        
        for col in categorical_columns:
            if col in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self.label_encoders[col] = le
        
        df_encoded['Age'] = self.scaler.fit_transform(df_encoded[['Age']])
        return df_encoded
    
    def prepare_training_data(self, df_encoded):
        """Chuẩn bị dữ liệu training"""
        X = df_encoded[self.feature_columns].values
        y_condition = self.condition_encoder.fit_transform(df_encoded['Medical Condition'])
        y_medication = self.medication_encoder.fit_transform(df_encoded['Medication'])
        return X, y_condition, y_medication
    
    def train_models(self, X, y_condition, y_medication):
        """Training các models"""
        X_train, X_test, y_cond_train, y_cond_test, y_med_train, y_med_test = train_test_split(
            X, y_condition, y_medication, test_size=0.2, random_state=42
        )
        
        self.condition_model.fit(X_train, y_cond_train)
        self.medication_model.fit(X_train, y_med_train)
        
        cond_pred = self.condition_model.predict(X_test)
        cond_accuracy = accuracy_score(y_cond_test, cond_pred)
        
        med_pred = self.medication_model.predict(X_test)
        med_accuracy = accuracy_score(y_med_test, med_pred)
        
        return cond_accuracy, med_accuracy
    
    def save_models(self):
        """Lưu models và encoders"""
        try:
            with open('simple_models.pkl', 'wb') as f:
                pickle.dump({
                    'condition_model': self.condition_model,
                    'medication_model': self.medication_model,
                    'label_encoders': self.label_encoders,
                    'scaler': self.scaler,
                    'condition_encoder': self.condition_encoder,
                    'medication_encoder': self.medication_encoder
                }, f)
            return True
        except:
            return False
    
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
            return True
        except:
            return False
    
    def predict(self, age, gender, blood_type, admission_type, test_results):
        """Dự đoán cho bệnh nhân mới"""
        try:
            input_data = {
                'Age': [age],
                'Gender': [gender],
                'Blood Type': [blood_type], 
                'Admission Type': [admission_type],
                'Test Results': [test_results]
            }
            
            df_input = pd.DataFrame(input_data)
            
            for col in ['Gender', 'Blood Type', 'Admission Type', 'Test Results']:
                if col in self.label_encoders:
                    try:
                        df_input[col] = self.label_encoders[col].transform(df_input[col])
                    except:
                        df_input[col] = 0
            
            df_input['Age'] = self.scaler.transform(df_input[['Age']])
            X_input = df_input[self.feature_columns].values
            
            condition_pred = self.condition_model.predict(X_input)[0]
            medication_pred = self.medication_model.predict(X_input)[0]
            
            condition_proba = np.max(self.condition_model.predict_proba(X_input)[0])
            medication_proba = np.max(self.medication_model.predict_proba(X_input)[0])
            
            predicted_condition = self.condition_encoder.inverse_transform([condition_pred])[0]
            predicted_medication = self.medication_encoder.inverse_transform([medication_pred])[0]
            
            return {
                'condition': predicted_condition,
                'condition_confidence': condition_proba,
                'medication': predicted_medication,
                'medication_confidence': medication_proba
            }
            
        except Exception as e:
            return None

# Khởi tạo chatbot
@st.cache_resource
def init_chatbot():
    chatbot = StreamlitHealthcareChatbot()
    
    if not chatbot.load_models():
        st.info("🔄 Đang training model lần đầu...")
        
        if os.path.exists('healthcare_dataset.csv'):
            df = chatbot.load_and_preprocess_data('healthcare_dataset.csv', sample_size=1000)
            if df is not None:
                df_encoded = chatbot.encode_features(df)
                X, y_condition, y_medication = chatbot.prepare_training_data(df_encoded)
                cond_acc, med_acc = chatbot.train_models(X, y_condition, y_medication)
                
                if chatbot.save_models():
                    st.success(f"✅ Training hoàn thành! Độ chính xác: Bệnh {cond_acc:.1%}, Thuốc {med_acc:.1%}")
                else:
                    st.error("❌ Lỗi lưu model")
            else:
                st.error("❌ Không thể tải dữ liệu")
        else:
            st.error("❌ Không tìm thấy file healthcare_dataset.csv")
    
    return chatbot

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare AI Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="sub-header">Hệ thống dự đoán tình trạng sức khỏe thông minh</h3>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📋 Thông tin hệ thống")
    st.sidebar.info("""
    **🤖 Healthcare Chatbot**
    
    Hệ thống AI giúp dự đoán:
    - 🏥 Tình trạng bệnh
    - 💊 Thuốc phù hợp
    
    Dựa trên thông tin:
    - 👤 Thông tin cá nhân
    - 🩸 Nhóm máu
    - 📊 Kết quả xét nghiệm
    """)
    
    st.sidebar.warning("⚠️ **Lưu ý quan trọng**: Kết quả chỉ mang tính chất tham khảo. Vui lòng tham khảo ý kiến bác sĩ!")
    
    # Khởi tạo chatbot
    chatbot = init_chatbot()
    
    # Tạo tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Dự đoán", "📊 Dữ liệu mẫu", "📈 Thống kê"])
    
    with tab1:
        st.header("🔍 Dự đoán tình trạng sức khỏe")
        
        # Form nhập liệu
        with st.form("prediction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("👤 Tuổi", min_value=1, max_value=120, value=30, step=1)
                gender = st.selectbox("⚤ Giới tính", ["Male", "Female"])
                blood_type = st.selectbox("🩸 Nhóm máu", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            
            with col2:
                admission_type = st.selectbox("🏥 Loại nhập viện", ["Emergency", "Urgent", "Elective"])
                test_results = st.selectbox("📊 Kết quả xét nghiệm", ["Normal", "Abnormal", "Inconclusive"])
            
            submitted = st.form_submit_button("🔮 Dự đoán", type="primary")
            
            if submitted:
                with st.spinner("🤔 Đang phân tích..."):
                    result = chatbot.predict(age, gender, blood_type, admission_type, test_results)
                    
                    if result:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.success("✅ Dự đoán hoàn thành!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(
                                label="🏥 Tình trạng bệnh dự đoán",
                                value=result['condition'],
                                delta=f"Tin cậy: {result['condition_confidence']:.1%}"
                            )
                        
                        with col2:
                            st.metric(
                                label="💊 Thuốc đề xuất",
                                value=result['medication'],
                                delta=f"Tin cậy: {result['medication_confidence']:.1%}"
                            )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Biểu đồ confidence
                        confidence_data = pd.DataFrame({
                            'Loại dự đoán': ['Tình trạng bệnh', 'Thuốc'],
                            'Độ tin cậy': [result['condition_confidence'], result['medication_confidence']]
                        })
                        
                        st.bar_chart(confidence_data.set_index('Loại dự đoán'))
                        
                    else:
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error("❌ Không thể thực hiện dự đoán. Vui lòng thử lại!")
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.header("📊 Dữ liệu mẫu")
        
        if st.button("🎲 Tạo dự đoán mẫu"):
            samples = [
                (45, "Male", "A+", "Emergency", "Abnormal"),
                (60, "Female", "O-", "Urgent", "Normal"),
                (25, "Male", "B+", "Elective", "Inconclusive"),
                (70, "Female", "AB+", "Emergency", "Abnormal"),
                (35, "Female", "A-", "Urgent", "Normal")
            ]
            
            results = []
            for age, gender, blood, admission, test in samples:
                result = chatbot.predict(age, gender, blood, admission, test)
                if result:
                    results.append({
                        'Tuổi': age,
                        'Giới tính': gender,
                        'Nhóm máu': blood,
                        'Loại nhập viện': admission,
                        'Kết quả XN': test,
                        'Dự đoán bệnh': result['condition'],
                        'Tin cậy (%)': f"{result['condition_confidence']:.1%}",
                        'Thuốc đề xuất': result['medication'],
                        'Tin cậy thuốc (%)': f"{result['medication_confidence']:.1%}"
                    })
            
            if results:
                df_results = pd.DataFrame(results)
                st.dataframe(df_results, use_container_width=True)
                
                # Download CSV
                csv = df_results.to_csv(index=False)
                st.download_button(
                    label="📥 Tải về CSV",
                    data=csv,
                    file_name="healthcare_predictions.csv",
                    mime="text/csv"
                )
    
    with tab3:
        st.header("📈 Thống kê hệ thống")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Dữ liệu training", "1,000", "samples")
        
        with col2:
            st.metric("🎯 Model accuracy", "~15-20%", "tương đối")
        
        with col3:
            st.metric("🚀 Tốc độ dự đoán", "< 1s", "nhanh")
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.info("""
        **📋 Thông tin kỹ thuật:**
        - **Algorithm**: Random Forest Classifier
        - **Features**: Tuổi, giới tính, nhóm máu, loại nhập viện, kết quả xét nghiệm
        - **Training data**: 1000 samples từ healthcare dataset
        - **Models**: 2 models riêng biệt cho dự đoán bệnh và thuốc
        """)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 