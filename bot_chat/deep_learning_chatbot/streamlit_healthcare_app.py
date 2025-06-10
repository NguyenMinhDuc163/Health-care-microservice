import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

# Cấu hình trang
st.set_page_config(
    page_title="🏥 Healthcare AI Chatbot",
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
    .result-box {
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #4CAF50;
        background: linear-gradient(135deg, #f1f8e9, #e8f5e8);
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .warning-box {
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ff9800;
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class StreamlitHealthcareChatbot:
    def __init__(self):
        self.condition_model = None
        self.medication_model = None
        self.label_encoders = {}
        self.scaler = None
        self.condition_encoder = None
        self.medication_encoder = None
        self.feature_columns = [
            'Age', 'Gender', 'Blood Type', 'Admission Type', 
            'Test Results', 'Age_Group', 'Risk_Score'
        ]
        self.model_metrics = {}
        
    def load_models(self, model_dir='models'):
        """Tải models đã được training"""
        try:
            metadata_path = os.path.join(model_dir, 'latest_metadata.pkl')
            
            if not os.path.exists(metadata_path):
                return False
            
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Tải models
            with open(metadata['condition_model_path'], 'rb') as f:
                self.condition_model = pickle.load(f)
            with open(metadata['medication_model_path'], 'rb') as f:
                self.medication_model = pickle.load(f)
            
            # Tải encoders
            self.label_encoders = metadata['label_encoders']
            self.scaler = metadata['scaler']
            self.condition_encoder = metadata['condition_encoder']
            self.medication_encoder = metadata['medication_encoder']
            self.feature_columns = metadata['feature_columns']
            self.model_metrics = metadata.get('model_metrics', {})
            
            return True
            
        except Exception as e:
            st.error(f"❌ Lỗi tải models: {str(e)}")
            return False
    
    def predict_with_confidence(self, age, gender, blood_type, admission_type, test_results, top_k=3):
        """Dự đoán với confidence scores"""
        try:
            # Feature engineering
            if age < 18:
                age_group = 'Child'
            elif age < 35:
                age_group = 'Young_Adult'
            elif age < 50:
                age_group = 'Adult'
            elif age < 65:
                age_group = 'Middle_Age'
            else:
                age_group = 'Senior'
            
            # Risk score calculation
            risk_score = (age / 100) * 0.3
            risk_score += {'Normal': 0.1, 'Inconclusive': 0.5, 'Abnormal': 0.9}.get(test_results, 0.5) * 0.4
            risk_score += {'Elective': 0.2, 'Urgent': 0.6, 'Emergency': 1.0}.get(admission_type, 0.5) * 0.3
            
            # Chuẩn bị input data
            input_data = {
                'Age': [age],
                'Gender': [gender],
                'Blood Type': [blood_type], 
                'Admission Type': [admission_type],
                'Test Results': [test_results],
                'Age_Group': [age_group],
                'Risk_Score': [risk_score]
            }
            
            df_input = pd.DataFrame(input_data)
            
            # Encode categorical features
            for col in ['Gender', 'Blood Type', 'Admission Type', 'Test Results', 'Age_Group']:
                if col in self.label_encoders:
                    try:
                        df_input[col] = self.label_encoders[col].transform(df_input[col])
                    except ValueError:
                        df_input[col] = 0
            
            # Scale numerical features
            numerical_cols = ['Age', 'Risk_Score']
            df_input[numerical_cols] = self.scaler.transform(df_input[numerical_cols])
            
            X_input = df_input[self.feature_columns].values
            
            # Dự đoán với probability
            condition_proba = self.condition_model.predict_proba(X_input)[0]
            medication_proba = self.medication_model.predict_proba(X_input)[0]
            
            # Top-k predictions
            condition_top_k = np.argsort(condition_proba)[-top_k:][::-1]
            medication_top_k = np.argsort(medication_proba)[-top_k:][::-1]
            
            # Chuyển đổi về tên gốc
            condition_predictions = []
            for idx in condition_top_k:
                condition_name = self.condition_encoder.inverse_transform([idx])[0]
                confidence = condition_proba[idx]
                condition_predictions.append({
                    'condition': condition_name,
                    'confidence': confidence
                })
            
            medication_predictions = []
            for idx in medication_top_k:
                medication_name = self.medication_encoder.inverse_transform([idx])[0]
                confidence = medication_proba[idx]
                medication_predictions.append({
                    'medication': medication_name,
                    'confidence': confidence
                })
            
            return {
                'condition_predictions': condition_predictions,
                'medication_predictions': medication_predictions,
                'risk_score': risk_score,
                'age_group': age_group,
                'input_processed': True
            }
            
        except Exception as e:
            return None

# Khởi tạo chatbot
@st.cache_resource
def init_chatbot():
    """Khởi tạo và load chatbot"""
    chatbot = StreamlitHealthcareChatbot()
    
    if chatbot.load_models():
        return chatbot, True
    else:
        return chatbot, False

def main():
    """Hàm main cho Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare AI Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('### Hệ thống dự đoán tình trạng sức khỏe thông minh với Ensemble Learning')
    
    # Khởi tạo chatbot
    chatbot, model_loaded = init_chatbot()
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Thông tin hệ thống")
        
        if model_loaded:
            st.success("✅ Models đã được tải thành công!")
            
            if chatbot.model_metrics:
                st.markdown("### 📊 Hiệu suất Models")
                st.metric("🏥 Condition Accuracy", f"{chatbot.model_metrics.get('condition_accuracy', 0):.1%}")
                st.metric("💊 Medication Accuracy", f"{chatbot.model_metrics.get('medication_accuracy', 0):.1%}")
                st.metric("🎯 Training Samples", f"{chatbot.model_metrics.get('training_samples', 0):,}")
        else:
            st.error("❌ Chưa có models được training!")
            st.info("Vui lòng chạy `python chatbot.py` để training models trước.")
        
        st.markdown("### 🤖 Công nghệ")
        st.info("""
        **Ensemble Learning:**
        - 🌳 Random Forest
        - 🚀 Gradient Boosting
        - 🧠 MLP Neural Network
        - 🗳️ Voting Classifier
        """)
        
        st.warning("⚠️ **Lưu ý**: Kết quả chỉ mang tính chất tham khảo!")
    
    # Main content
    if not model_loaded:
        st.error("### ❌ Models chưa sẵn sàng")
        st.info("Hãy chạy training trước: `python chatbot.py`")
        return
    
    # Tạo tabs
    tab1, tab2 = st.tabs(["🔍 Dự đoán", "📊 Dữ liệu mẫu"])
    
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
            
            submitted = st.form_submit_button("🔮 Dự đoán", type="primary", use_container_width=True)
            
            if submitted:
                with st.spinner("🤔 Đang phân tích dữ liệu..."):
                    result = chatbot.predict_with_confidence(age, gender, blood_type, admission_type, test_results, top_k=3)
                    
                    if result:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.success("✅ Dự đoán hoàn thành!")
                        
                        # Hiển thị thông tin
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("### 👤 Thông tin")
                            st.write(f"**Tuổi**: {age}")
                            st.write(f"**Giới tính**: {gender}")
                            st.write(f"**Nhóm máu**: {blood_type}")
                        
                        with col2:
                            st.markdown("### 🏥 Y tế")
                            st.write(f"**Nhập viện**: {admission_type}")
                            st.write(f"**Xét nghiệm**: {test_results}")
                            st.write(f"**Nhóm tuổi**: {result['age_group']}")
                        
                        with col3:
                            st.markdown("### ⚠️ Risk")
                            risk_color = "🟢" if result['risk_score'] < 0.3 else "🟡" if result['risk_score'] < 0.7 else "🔴"
                            st.write(f"**Risk Score**: {risk_color} {result['risk_score']:.2f}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Kết quả dự đoán
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 🏥 Dự đoán tình trạng bệnh (Top 3)")
                            for i, pred in enumerate(result['condition_predictions'], 1):
                                confidence_color = "🟢" if pred['confidence'] > 0.7 else "🟡" if pred['confidence'] > 0.4 else "🔴"
                                st.write(f"**{i}. {pred['condition']}** {confidence_color} {pred['confidence']:.1%}")
                        
                        with col2:
                            st.markdown("### 💊 Đề xuất thuốc (Top 3)")
                            for i, pred in enumerate(result['medication_predictions'], 1):
                                confidence_color = "🟢" if pred['confidence'] > 0.7 else "🟡" if pred['confidence'] > 0.4 else "🔴"
                                st.write(f"**{i}. {pred['medication']}** {confidence_color} {pred['confidence']:.1%}")
                        
                        # Cảnh báo
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.warning("""
                        ### ⚠️ LƯU Ý QUAN TRỌNG:
                        - 🏥 Kết quả chỉ mang tính chất **tham khảo**
                        - 👨‍⚕️ **Bắt buộc** tham khảo ý kiến bác sĩ chuyên khoa
                        - 💊 **Không tự ý** sử dụng thuốc khi chưa được chỉ định
                        """)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    else:
                        st.error("❌ Không thể thực hiện dự đoán. Vui lòng thử lại!")
    
    with tab2:
        st.header("📊 Dữ liệu mẫu")
        
        if st.button("🎲 Chạy dự đoán cho 5 trường hợp mẫu", type="primary"):
            samples = [
                (45, "Male", "A+", "Emergency", "Abnormal", "👨 Người đàn ông trung niên cấp cứu"),
                (67, "Female", "O-", "Urgent", "Abnormal", "👵 Phụ nữ cao tuổi nhập viện khẩn cấp"),
                (25, "Male", "B+", "Elective", "Normal", "👦 Thanh niên khám tổng quát"),
                (55, "Female", "AB+", "Urgent", "Inconclusive", "👩 Phụ nữ trung niên"),
                (8, "Male", "O+", "Emergency", "Abnormal", "👶 Trẻ em cấp cứu")
            ]
            
            results_data = []
            
            for i, (age, gender, blood, admission, test, description) in enumerate(samples, 1):
                st.markdown(f"### {description}")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write(f"**Tuổi**: {age}")
                    st.write(f"**Giới tính**: {gender}")
                    st.write(f"**Nhóm máu**: {blood}")
                    st.write(f"**Nhập viện**: {admission}")
                    st.write(f"**Xét nghiệm**: {test}")
                
                with col2:
                    result = chatbot.predict_with_confidence(age, gender, blood, admission, test, top_k=2)
                    
                    if result:
                        top_condition = result['condition_predictions'][0]
                        top_medication = result['medication_predictions'][0]
                        
                        st.success(f"🏥 **Dự đoán**: {top_condition['condition']} ({top_condition['confidence']:.1%})")
                        st.info(f"💊 **Thuốc**: {top_medication['medication']} ({top_medication['confidence']:.1%})")
                        
                        risk_color = "🟢 Thấp" if result['risk_score'] < 0.3 else "🟡 Trung bình" if result['risk_score'] < 0.7 else "🔴 Cao"
                        st.warning(f"⚠️ **Risk**: {risk_color} ({result['risk_score']:.2f})")
                    else:
                        st.error("❌ Lỗi dự đoán")
                
                st.divider()

if __name__ == "__main__":
    main() 