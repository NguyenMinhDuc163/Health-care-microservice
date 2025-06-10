import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit, GridSearchCV, cross_val_score
from sklearn.preprocessing import LabelEncoder, RobustScaler, StandardScaler
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, top_k_accuracy_score
from sklearn.utils.class_weight import compute_class_weight
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("🚀 Sử dụng Advanced Machine Learning với Python 3.13.2")
print("🧠 Models: RandomForest + GradientBoosting + MLPClassifier + Ensemble")

class ProfessionalHealthcareChatbot:
    def __init__(self):
        self.condition_model = None
        self.medication_model = None
        self.label_encoders = {}
        self.scaler = RobustScaler()  # Robust hơn StandardScaler
        self.condition_encoder = LabelEncoder()
        self.medication_encoder = LabelEncoder()
        
        # Feature engineering - thêm nhiều features hơn
        self.feature_columns = [
            'Age', 'Gender', 'Blood Type', 'Admission Type', 
            'Test Results', 'Age_Group', 'Risk_Score'
        ]
        
        # Thông tin training
        self.training_history = None
        self.model_metrics = {}
        
    def load_and_preprocess_data(self, file_path, use_full_data=True):
        """Tải và xử lý toàn bộ dữ liệu healthcare"""
        print("🔄 Đang tải dữ liệu healthcare...")
        
        try:
            if use_full_data:
                # Tải toàn bộ dữ liệu
                df = pd.read_csv(file_path)
                print(f"📊 Đã tải TOÀN BỘ dữ liệu: {len(df)} bản ghi")
            else:
                # Tải sample để test nhanh
                df = pd.read_csv(file_path, nrows=5000)
                print(f"📊 Đã tải sample: {len(df)} bản ghi")
            
            # Thống kê dữ liệu ban đầu
            print(f"📋 Kích thước dữ liệu: {df.shape}")
            print(f"📋 Các cột: {list(df.columns)}")
            print(f"📋 Dữ liệu thiếu: {df.isnull().sum().sum()} cells")
            
            # Làm sạch dữ liệu
            initial_count = len(df)
            df = df.dropna()
            final_count = len(df)
            print(f"📊 Sau khi loại bỏ dữ liệu thiếu: {final_count} bản ghi ({initial_count - final_count} đã bị loại bỏ)")
            
            # Chuẩn hóa tên cột
            df.columns = df.columns.str.strip()
            
            # Thống kê phân bố dữ liệu
            print("\n📈 PHÂN BỐ DỮ LIỆU:")
            print(f"   • Số lượng bệnh khác nhau: {df['Medical Condition'].nunique()}")
            print(f"   • Số lượng thuốc khác nhau: {df['Medication'].nunique()}")
            print(f"   • Độ tuổi: {df['Age'].min()}-{df['Age'].max()} (trung bình: {df['Age'].mean():.1f})")
            print(f"   • Giới tính: {df['Gender'].value_counts().to_dict()}")
            
            return df
            
        except Exception as e:
            print(f"❌ Lỗi tải dữ liệu: {str(e)}")
            return None
    
    def feature_engineering(self, df):
        """Tạo thêm các features từ dữ liệu gốc"""
        print("🔧 Đang thực hiện feature engineering...")
        
        df_enhanced = df.copy()
        
        # 1. Tạo Age Groups
        df_enhanced['Age_Group'] = pd.cut(
            df_enhanced['Age'], 
            bins=[0, 18, 35, 50, 65, 100], 
            labels=['Child', 'Young_Adult', 'Adult', 'Middle_Age', 'Senior']
        )
        
        # 2. Tạo Risk Score dựa trên nhiều yếu tố
        risk_score = 0
        
        # Risk từ tuổi
        risk_score += (df_enhanced['Age'] / 100) * 0.3
        
        # Risk từ kết quả xét nghiệm
        risk_score += df_enhanced['Test Results'].map({
            'Normal': 0.1, 'Inconclusive': 0.5, 'Abnormal': 0.9
        }).fillna(0.5) * 0.4
        
        # Risk từ loại nhập viện
        risk_score += df_enhanced['Admission Type'].map({
            'Elective': 0.2, 'Urgent': 0.6, 'Emergency': 1.0
        }).fillna(0.5) * 0.3
        
        df_enhanced['Risk_Score'] = risk_score
        
        print(f"✅ Đã tạo thêm {len(['Age_Group', 'Risk_Score'])} features")
        return df_enhanced
    
    def encode_features(self, df):
        """Mã hóa các đặc trưng categorical với kỹ thuật tiên tiến"""
        print("🔄 Đang mã hóa dữ liệu với kỹ thuật tiên tiến...")
        
        df_encoded = df.copy()
        
        # Mã hóa categorical columns
        categorical_columns = ['Gender', 'Blood Type', 'Admission Type', 'Test Results', 'Age_Group']
        
        for col in categorical_columns:
            if col in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self.label_encoders[col] = le
                print(f"   ✓ Encoded {col}: {len(le.classes_)} classes")
        
        # Chuẩn hóa numerical features với RobustScaler
        numerical_cols = ['Age', 'Risk_Score']
        df_encoded[numerical_cols] = self.scaler.fit_transform(df_encoded[numerical_cols])
        
        return df_encoded
    
    def prepare_training_data(self, df_encoded):
        """Chuẩn bị dữ liệu training với class balancing"""
        print("📊 Đang chuẩn bị dữ liệu training...")
        
        # Features (X)
        X = df_encoded[self.feature_columns].values
        print(f"   ✓ Features shape: {X.shape}")
        
        # Targets (y)
        y_condition = self.condition_encoder.fit_transform(df_encoded['Medical Condition'])
        y_medication = self.medication_encoder.fit_transform(df_encoded['Medication'])
        
        print(f"   ✓ Condition classes: {len(self.condition_encoder.classes_)}")
        print(f"   ✓ Medication classes: {len(self.medication_encoder.classes_)}")
        
        # Class weights để xử lý imbalanced data
        condition_weights = compute_class_weight('balanced', classes=np.unique(y_condition), y=y_condition)
        medication_weights = compute_class_weight('balanced', classes=np.unique(y_medication), y=y_medication)
        
        self.condition_class_weights = dict(enumerate(condition_weights))
        self.medication_class_weights = dict(enumerate(medication_weights))
        
        return X, y_condition, y_medication
    
    def build_advanced_ensemble(self, model_name='model'):
        """Xây dựng ensemble model tiên tiến với ML algorithms"""
        print(f"🏗️ Xây dựng {model_name} với Ensemble Learning...")
        
        # 1. Random Forest với hyperparameter tuning
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        
        # 2. Gradient Boosting
        gb_model = GradientBoostingClassifier(
            n_estimators=150,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42
        )
        
        # 3. MLP Neural Network
        mlp_model = MLPClassifier(
            hidden_layer_sizes=(256, 128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            learning_rate_init=0.001,
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=20
        )
        
        # 4. Ensemble với Voting
        ensemble_model = VotingClassifier(
            estimators=[
                ('rf', rf_model),
                ('gb', gb_model), 
                ('mlp', mlp_model)
            ],
            voting='soft'  # Sử dụng probability voting
        )
        
        print(f"   ✓ Ensemble gồm 3 models: RandomForest + GradientBoosting + MLP")
        return ensemble_model
    
    def train_advanced_models(self, X, y_condition, y_medication, use_cross_validation=True):
        """Training ensemble models với kỹ thuật ML tiên tiến"""
        print("🚀 Bắt đầu training Ensemble Models với Advanced ML...")
        
        # Chia dữ liệu với stratified split để đảm bảo phân bố đều
        sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        train_idx, test_idx = next(sss.split(X, y_condition))
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_cond_train, y_cond_test = y_condition[train_idx], y_condition[test_idx]
        y_med_train, y_med_test = y_medication[train_idx], y_medication[test_idx]
        
        print(f"   📊 Training set: {len(X_train)} samples")
        print(f"   📊 Test set: {len(X_test)} samples")
        
        # === TRAINING CONDITION MODEL ===
        print("\n🏥 Training Ensemble Model Dự đoán Tình trạng Bệnh...")
        self.condition_model = self.build_advanced_ensemble('Condition Ensemble')
        
        # Cross-validation trước khi training
        if use_cross_validation and len(X_train) > 1000:
            print("   🔄 Thực hiện Cross-Validation...")
            cv_scores = cross_val_score(self.condition_model, X_train, y_cond_train, cv=3, scoring='accuracy', n_jobs=-1)
            print(f"   📊 CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Training model
        print("   🚀 Training...")
        self.condition_model.fit(X_train, y_cond_train)
        
        # === TRAINING MEDICATION MODEL ===
        print("\n💊 Training Ensemble Model Đề xuất Thuốc...")
        self.medication_model = self.build_advanced_ensemble('Medication Ensemble')
        
        # Cross-validation
        if use_cross_validation and len(X_train) > 1000:
            print("   🔄 Thực hiện Cross-Validation...")
            cv_scores = cross_val_score(self.medication_model, X_train, y_med_train, cv=3, scoring='accuracy', n_jobs=-1)
            print(f"   📊 CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Training model
        print("   🚀 Training...")
        self.medication_model.fit(X_train, y_med_train)
        
        # === ĐÁNH GIÁ MODELS ===
        print("\n📊 ĐÁNH GIÁ HIỆU QUẢ ENSEMBLE MODELS:")
        
        # Condition model evaluation
        cond_pred = self.condition_model.predict(X_test)
        cond_accuracy = accuracy_score(y_cond_test, cond_pred)
        
        # Medication model evaluation
        med_pred = self.medication_model.predict(X_test)
        med_accuracy = accuracy_score(y_med_test, med_pred)
        
        # Top-3 accuracy calculation
        cond_proba = self.condition_model.predict_proba(X_test)
        med_proba = self.medication_model.predict_proba(X_test)
        
        # Calculate top-3 accuracy manually
        cond_top3_acc = self._calculate_top_k_accuracy(y_cond_test, cond_proba, k=3)
        med_top3_acc = self._calculate_top_k_accuracy(y_med_test, med_proba, k=3)
        
        # Feature importance analysis
        self._analyze_feature_importance()
        
        self.model_metrics = {
            'condition_accuracy': cond_accuracy,
            'medication_accuracy': med_accuracy,
            'condition_top3_accuracy': cond_top3_acc,
            'medication_top3_accuracy': med_top3_acc,
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        print(f"🎯 Độ chính xác dự đoán tình trạng bệnh: {cond_accuracy:.3f} ({cond_accuracy:.1%})")
        print(f"🎯 Top-3 accuracy tình trạng bệnh: {cond_top3_acc:.3f} ({cond_top3_acc:.1%})")
        print(f"💊 Độ chính xác đề xuất thuốc: {med_accuracy:.3f} ({med_accuracy:.1%})")
        print(f"💊 Top-3 accuracy thuốc: {med_top3_acc:.3f} ({med_top3_acc:.1%})")
        
        return True, True
    
    def _calculate_top_k_accuracy(self, y_true, y_proba, k=3):
        """Tính toán top-k accuracy"""
        top_k_pred = np.argsort(y_proba, axis=1)[:, -k:]
        correct = 0
        for i, true_label in enumerate(y_true):
            if true_label in top_k_pred[i]:
                correct += 1
        return correct / len(y_true)
    
    def _analyze_feature_importance(self):
        """Phân tích feature importance"""
        print("\n🔍 PHÂN TÍCH FEATURE IMPORTANCE:")
        
        # Lấy feature importance từ Random Forest
        if hasattr(self.condition_model, 'named_estimators_'):
            rf_model = self.condition_model.named_estimators_['rf']
            feature_importance = rf_model.feature_importances_
            
            importance_dict = dict(zip(self.feature_columns, feature_importance))
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            print("   📊 Top features cho dự đoán bệnh:")
            for feature, importance in sorted_features:
                print(f"      • {feature}: {importance:.3f}")
        else:
            print("   ⚠️  Feature importance chỉ khả dụng cho ensemble models")
    
    def save_models(self, model_dir='models'):
        """Lưu models và metadata với timestamp"""
        print("💾 Đang lưu models và metadata...")
        
        # Tạo thư mục models nếu chưa có
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Lưu models (pickle format)
        condition_path = os.path.join(model_dir, f'condition_model_{timestamp}.pkl')
        medication_path = os.path.join(model_dir, f'medication_model_{timestamp}.pkl')
        
        with open(condition_path, 'wb') as f:
            pickle.dump(self.condition_model, f)
        with open(medication_path, 'wb') as f:
            pickle.dump(self.medication_model, f)
        
        # Lưu encoders và metadata
        metadata = {
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'condition_encoder': self.condition_encoder,
            'medication_encoder': self.medication_encoder,
            'feature_columns': self.feature_columns,
            'model_metrics': self.model_metrics,
            'timestamp': timestamp,
            'condition_model_path': condition_path,
            'medication_model_path': medication_path
        }
        
        metadata_path = os.path.join(model_dir, f'metadata_{timestamp}.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        # Lưu phiên bản mới nhất
        with open(os.path.join(model_dir, 'latest_metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"✅ Đã lưu models và metadata vào {model_dir}/")
        print(f"   • Condition model: {condition_path}")
        print(f"   • Medication model: {medication_path}")
        print(f"   • Metadata: {metadata_path}")
        
    def load_models(self, model_dir='models', use_latest=True):
        """Tải models đã lưu"""
        try:
            metadata_path = os.path.join(model_dir, 'latest_metadata.pkl') if use_latest else None
            
            if not metadata_path or not os.path.exists(metadata_path):
                print("❌ Không tìm thấy models đã lưu.")
                return False
            
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Tải models (pickle format thay vì h5)
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
            
            print(f"✅ Đã tải ensemble models thành công! (Timestamp: {metadata['timestamp']})")
            if self.model_metrics:
                print(f"   📊 Condition accuracy: {self.model_metrics.get('condition_accuracy', 0):.1%}")
                print(f"   📊 Medication accuracy: {self.model_metrics.get('medication_accuracy', 0):.1%}")
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi tải models: {str(e)}")
            return False
    
    def predict_with_confidence(self, age, gender, blood_type, admission_type, test_results, top_k=3):
        """Dự đoán với confidence scores và top-k results"""
        if self.condition_model is None or self.medication_model is None:
            return "❌ Models chưa được training!"
        
        try:
            # Feature engineering cho input
            age_group = 'Child' if age < 18 else 'Young_Adult' if age < 35 else 'Adult' if age < 50 else 'Middle_Age' if age < 65 else 'Senior'
            
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
                        # Nếu giá trị mới không có trong training data
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
            return f"❌ Lỗi dự đoán: {str(e)}"
    
    def interactive_chat(self):
        """Interface chat chuyên nghiệp với nhiều tính năng"""
        print("\n" + "="*60)
        print("🏥 PROFESSIONAL HEALTHCARE AI CHATBOT")
        print("="*60)
        print("🤖 Chào mừng đến với Healthcare AI Chatbot chuyên nghiệp!")
        print("🎯 Tôi có thể dự đoán tình trạng bệnh và đề xuất thuốc với độ chính xác cao.")
        
        if self.model_metrics:
            print(f"📊 Hiệu suất model: Condition {self.model_metrics.get('condition_accuracy', 0):.1%}, Medication {self.model_metrics.get('medication_accuracy', 0):.1%}")
        
        print("\n📋 Lệnh có sẵn:")
        print("   • 'predict' - Dự đoán cho bệnh nhân mới")
        print("   • 'batch' - Dự đoán hàng loạt")
        print("   • 'stats' - Xem thống kê model")
        print("   • 'help' - Xem hướng dẫn")
        print("   • 'quit' - Thoát chương trình")
        print()
        
        while True:
            command = input("💬 Nhập lệnh (predict/batch/stats/help/quit): ").lower().strip()
            
            if command == 'quit':
                print("\n👋 Cảm ơn bạn đã sử dụng Healthcare AI Chatbot!")
                break
                
            elif command == 'predict':
                self._handle_single_prediction()
                
            elif command == 'batch':
                self._handle_batch_prediction()
                
            elif command == 'stats':
                self._show_model_stats()
                
            elif command == 'help':
                self._show_help()
                
            else:
                print("❌ Lệnh không hợp lệ. Nhập 'help' để xem hướng dẫn.")
    
    def _handle_single_prediction(self):
        """Xử lý dự đoán đơn lẻ"""
        print("\n📝 NHẬP THÔNG TIN BỆNH NHÂN:")
        print("-" * 40)
        
        try:
            age = int(input("👤 Tuổi (1-120): "))
            if not 1 <= age <= 120:
                print("❌ Tuổi phải từ 1-120!")
                return
            
            print("⚤  Giới tính:")
            print("   1. Male")
            print("   2. Female")
            gender_choice = input("   Chọn (1-2): ")
            gender = "Male" if gender_choice == "1" else "Female"
            
            print("🩸 Nhóm máu:")
            blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            for i, bt in enumerate(blood_types, 1):
                print(f"   {i}. {bt}")
            bt_choice = int(input("   Chọn (1-8): ")) - 1
            blood_type = blood_types[bt_choice]
            
            print("🏥 Loại nhập viện:")
            print("   1. Emergency")
            print("   2. Urgent") 
            print("   3. Elective")
            adm_choice = input("   Chọn (1-3): ")
            admission_types = ["Emergency", "Urgent", "Elective"]
            admission_type = admission_types[int(adm_choice) - 1]
            
            print("📊 Kết quả xét nghiệm:")
            print("   1. Normal")
            print("   2. Abnormal")
            print("   3. Inconclusive")
            test_choice = input("   Chọn (1-3): ")
            test_results_list = ["Normal", "Abnormal", "Inconclusive"]
            test_results = test_results_list[int(test_choice) - 1]
            
            # Dự đoán
            print("\n🤔 Đang phân tích...")
            result = self.predict_with_confidence(age, gender, blood_type, admission_type, test_results, top_k=3)
            
            if isinstance(result, dict):
                print("\n🔍 KẾT QUẢ DỰ ĐOÁN CHI TIẾT:")
                print("=" * 50)
                
                print(f"👤 Thông tin: {age} tuổi, {gender}, {blood_type}")
                print(f"🏥 Nhập viện: {admission_type}, XN: {test_results}")
                print(f"⚠️  Risk Score: {result['risk_score']:.2f}")
                print(f"👥 Nhóm tuổi: {result['age_group']}")
                
                print("\n🏥 DỰ ĐOÁN TÌNH TRẠNG BỆNH (Top 3):")
                for i, pred in enumerate(result['condition_predictions'], 1):
                    print(f"   {i}. {pred['condition']:<15} (Tin cậy: {pred['confidence']:.1%})")
                
                print("\n💊 ĐỀ XUẤT THUỐC (Top 3):")
                for i, pred in enumerate(result['medication_predictions'], 1):
                    print(f"   {i}. {pred['medication']:<15} (Tin cậy: {pred['confidence']:.1%})")
                
                print("\n⚠️  LƯU Ý QUAN TRỌNG:")
                print("   • Kết quả chỉ mang tính chất tham khảo")
                print("   • Vui lòng tham khảo ý kiến bác sĩ chuyên khoa")
                print("   • Không tự ý sử dụng thuốc khi chưa được chỉ định")
                
            else:
                print(f"❌ {result}")
                
        except (ValueError, IndexError):
            print("❌ Dữ liệu nhập không hợp lệ!")
        except KeyboardInterrupt:
            print("\n⏹️  Đã hủy thao tác.")
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
    
    def _handle_batch_prediction(self):
        """Xử lý dự đoán hàng loạt"""
        print("\n📊 DỰ ĐOÁN HÀNG LOẠT - 5 TRƯỜNG HỢP MẪU:")
        print("-" * 50)
        
        samples = [
            (45, "Male", "A+", "Emergency", "Abnormal", "Người đàn ông trung niên cấp cứu"),
            (67, "Female", "O-", "Urgent", "Abnormal", "Phụ nữ cao tuổi nhập viện khẩn cấp"),
            (25, "Male", "B+", "Elective", "Normal", "Thanh niên khám tổng quát"),
            (55, "Female", "AB+", "Urgent", "Inconclusive", "Phụ nữ trung niên, KQ không rõ ràng"),
            (8, "Male", "O+", "Emergency", "Abnormal", "Trẻ em cấp cứu")
        ]
        
        for i, (age, gender, blood, admission, test, description) in enumerate(samples, 1):
            print(f"\n🔸 TRƯỜNG HỢP {i}: {description}")
            print(f"   📋 Thông tin: {age} tuổi, {gender}, {blood}, {admission}, {test}")
            
            result = self.predict_with_confidence(age, gender, blood, admission, test, top_k=2)
            
            if isinstance(result, dict):
                top_condition = result['condition_predictions'][0]
                top_medication = result['medication_predictions'][0]
                
                print(f"   🏥 Dự đoán: {top_condition['condition']} ({top_condition['confidence']:.1%})")
                print(f"   💊 Thuốc: {top_medication['medication']} ({top_medication['confidence']:.1%})")
                print(f"   ⚠️  Risk: {result['risk_score']:.2f}")
            else:
                print(f"   ❌ Lỗi: {result}")
    
    def _show_model_stats(self):
        """Hiển thị thống kê model"""
        if not self.model_metrics:
            print("❌ Chưa có thông tin thống kê model!")
            return
        
        print("\n📈 THỐNG KÊ HIỆU SUẤT MODEL:")
        print("=" * 40)
        print(f"🎯 Độ chính xác dự đoán bệnh: {self.model_metrics.get('condition_accuracy', 0):.3f} ({self.model_metrics.get('condition_accuracy', 0):.1%})")
        print(f"🎯 Top-3 accuracy bệnh: {self.model_metrics.get('condition_top3_accuracy', 0):.3f} ({self.model_metrics.get('condition_top3_accuracy', 0):.1%})")
        print(f"💊 Độ chính xác đề xuất thuốc: {self.model_metrics.get('medication_accuracy', 0):.3f} ({self.model_metrics.get('medication_accuracy', 0):.1%})")
        print(f"💊 Top-3 accuracy thuốc: {self.model_metrics.get('medication_top3_accuracy', 0):.3f} ({self.model_metrics.get('medication_top3_accuracy', 0):.1%})")
        print(f"📊 Dữ liệu training: {self.model_metrics.get('training_samples', 0):,} samples")
        print(f"📊 Dữ liệu test: {self.model_metrics.get('test_samples', 0):,} samples")
        
        if hasattr(self, 'condition_encoder'):
            print(f"🏥 Số loại bệnh: {len(self.condition_encoder.classes_)}")
            print(f"💊 Số loại thuốc: {len(self.medication_encoder.classes_)}")
    
    def _show_help(self):
        """Hiển thị hướng dẫn sử dụng"""
        print("\n📖 HƯỚNG DẪN SỬ DỤNG:")
        print("=" * 40)
        print("🔸 predict: Dự đoán cho một bệnh nhân")
        print("   - Nhập thông tin theo hướng dẫn")
        print("   - Nhận kết quả top-3 với confidence score")
        print()
        print("🔸 batch: Xem ví dụ dự đoán hàng loạt")
        print("   - 5 trường hợp mẫu đa dạng")
        print("   - So sánh kết quả dự đoán")
        print()
        print("🔸 stats: Xem thống kê hiệu suất model")
        print("   - Độ chính xác của model")
        print("   - Thông tin về dữ liệu training")
        print()
        print("🔸 help: Hiển thị hướng dẫn này")
        print("🔸 quit: Thoát chương trình")
        print()
        print("⚠️  LƯU Ý: Kết quả chỉ mang tính tham khảo!")

def main():
    """Hàm main chuyên nghiệp"""
    print("🚀 KHỞI ĐỘNG PROFESSIONAL HEALTHCARE AI CHATBOT")
    print("=" * 60)
    
    chatbot = ProfessionalHealthcareChatbot()
    
    # Kiểm tra models đã có chưa
    if chatbot.load_models():
        print("✅ Đã tải models thành công!")
    else:
        print("🔄 Không tìm thấy models. Bắt đầu training từ đầu...")
        
        # Hỏi người dùng có muốn dùng toàn bộ dữ liệu không
        print("\n📊 CHỌN CHẾ ĐỘ TRAINING:")
        print("1. 🚀 Full Training (toàn bộ dữ liệu) - Độ chính xác cao nhất")
        print("2. ⚡ Quick Training (5000 samples) - Nhanh hơn để test")
        
        while True:
            choice = input("Chọn (1-2): ").strip()
            if choice in ['1', '2']:
                break
            print("❌ Vui lòng chọn 1 hoặc 2!")
        
        use_full_data = (choice == '1')
        
        print(f"\n🎯 Chế độ: {'Full Training' if use_full_data else 'Quick Training'}")
        print("🤖 Sử dụng Ensemble Learning: RandomForest + GradientBoosting + MLP")
        
        # Tải và xử lý dữ liệu
        df = chatbot.load_and_preprocess_data('healthcare_dataset.csv', use_full_data=use_full_data)
        
        if df is None:
            print("❌ Không thể tải dữ liệu. Kết thúc chương trình.")
            return
        
        # Feature engineering
        df_enhanced = chatbot.feature_engineering(df)
        
        # Encode features
        df_encoded = chatbot.encode_features(df_enhanced)
        
        # Chuẩn bị training data
        X, y_condition, y_medication = chatbot.prepare_training_data(df_encoded)
        
        # Training với confirmation
        print(f"\n⚠️  SẴN SÀNG TRAINING VỚI {len(X):,} SAMPLES")
        print("💡 Quá trình này có thể mất vài phút...")
        
        confirm = input("Tiếp tục? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Đã hủy training.")
            return
        
        # Bắt đầu training
        print(f"\n🚀 BẮT ĐẦU TRAINING...")
        start_time = datetime.now()
        
        try:
            chatbot.train_advanced_models(X, y_condition, y_medication)
            
            # Lưu models
            chatbot.save_models()
            
            end_time = datetime.now()
            training_time = end_time - start_time
            print(f"\n⏱️  Thời gian training: {training_time}")
            print("✅ Training hoàn thành!")
            
        except KeyboardInterrupt:
            print("\n⏹️  Training đã bị dừng bởi người dùng.")
            return
        except Exception as e:
            print(f"\n❌ Lỗi training: {str(e)}")
            return
    
    # Bắt đầu chat interface
    print("\n🎉 CHATBOT SẴN SÀNG PHỤC VỤ!")
    chatbot.interactive_chat()

if __name__ == "__main__":
    main()
