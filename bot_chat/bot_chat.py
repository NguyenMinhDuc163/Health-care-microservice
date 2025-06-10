# save as app.py
import streamlit as st
import json
import re
from difflib import SequenceMatcher
import random

# Configure page
st.set_page_config(
    page_title="COVID-19 Healthcare Assistant",
    page_icon="🦠",
    layout="wide"
)


# Load knowledge base
@st.cache_data
def load_knowledge_base():
    try:
        # Load all knowledge bases
        knowledge_bases = {}
        
        # Load COVID-19 knowledge base
        with open('data/covid.json', 'r', encoding='utf-8') as f:
            covid_kb = json.load(f)
            knowledge_bases["covid19"] = covid_kb["covid19_knowledge_base"]
            
        # Load Cold knowledge base
        with open('data/cold.json', 'r', encoding='utf-8') as f:
            cold_kb = json.load(f)
            knowledge_bases["cold"] = cold_kb
            
        # Load Allergy knowledge base
        with open('data/allergy.json', 'r', encoding='utf-8') as f:
            allergy_kb = json.load(f)
            knowledge_bases["allergy"] = allergy_kb
            
        # Load Flu knowledge base
        with open('data/flu.json', 'r', encoding='utf-8') as f:
            flu_kb = json.load(f)
            knowledge_bases["flu"] = flu_kb
            
        return knowledge_bases
    except FileNotFoundError as e:
        st.error(f"⚠️ Không tìm thấy file knowledge base: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("⚠️ Lỗi đọc file JSON. Vui lòng kiểm tra cú pháp file.")
        return None


# Load ontology data
@st.cache_data
def load_ontology_data():
    try:
        ontologies = {}
        
        # Load COVID-19 ontology
        with open('data/ontology/covid_ontology.json', 'r', encoding='utf-8') as f:
            covid_onto = json.load(f)
            ontologies["covid19"] = covid_onto
            
        # Load Cold ontology
        with open('data/ontology/cold_ontology.json', 'r', encoding='utf-8') as f:
            cold_onto = json.load(f)
            ontologies["cold"] = cold_onto
            
        # Load Allergy ontology
        with open('data/ontology/allergy_ontology.json', 'r', encoding='utf-8') as f:
            allergy_onto = json.load(f)
            ontologies["allergy"] = allergy_onto
            
        # Load Flu ontology
        with open('data/ontology/flu_ontology.json', 'r', encoding='utf-8') as f:
            flu_onto = json.load(f)
            ontologies["flu"] = flu_onto
            
        return ontologies
    except FileNotFoundError as e:
        st.error(f"⚠️ Không tìm thấy file ontology: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("⚠️ Lỗi đọc file ontology JSON. Vui lòng kiểm tra cú pháp file.")
        return None


# Similarity function for fuzzy matching
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# Phân tích ý định người dùng
def analyze_user_intent(user_input):
    """Phân tích ý định của người dùng từ câu hỏi"""
    user_input_lower = user_input.lower().strip()
    
    # Xử lý các intent cơ bản (social intents)
    social_intent_patterns = {
        "greeting": ["xin chào", "chào", "hello", "hi", "hey", "good morning", "good afternoon", 
                    "good evening", "chào bạn", "xin chào bạn", "chào bot"],
        "goodbye": ["tạm biệt", "bye", "goodbye", "see you", "hẹn gặp lại", "chào tạm biệt", 
                   "kết thúc", "thoát", "quit", "exit"],
        "thanks": ["cảm ơn", "thank you", "thanks", "cảm ơn bạn", "cảm ơn bot", "thanks bot"],
        "how_are_you": ["bạn khỏe không", "how are you", "bạn thế nào", "tình hình như thế nào"],
        "what_can_you_do": ["bạn có thể làm gì", "what can you do", "bạn hỗ trợ gì", 
                           "tôi có thể hỏi gì", "bạn biết gì", "giúp tôi gì được"],
        "ask_more": ["có gì khác không", "tôi muốn hỏi thêm", "còn gì nữa", "hỏi thêm", 
                    "anything else", "what else", "còn gì khác"],
        "compliment": ["bạn giỏi quá", "tuyệt vời", "great", "good job", "excellent", "hay quá"],
        "help": ["help", "giúp đỡ", "hướng dẫn", "trợ giúp", "hỗ trợ"]
    }
    
    # Kiểm tra social intents trước
    for intent, patterns in social_intent_patterns.items():
        for pattern in patterns:
            if pattern in user_input_lower:
                return intent
    
    # Kiểm tra nếu người dùng mô tả triệu chứng trực tiếp
    personal_symptoms_patterns = ["tôi bị", "em bị", "mình bị", "bị", "có triệu chứng", 
                                 "đang bị", "cảm thấy", "thấy", "i have", "i feel"]
    
    for pattern in personal_symptoms_patterns:
        if pattern in user_input_lower:
            # Kiểm tra xem có triệu chứng nào được đề cập không
            symptoms = extract_symptoms_from_input(user_input)
            if symptoms:
                return "symptom_analysis"
    
    # Intent patterns cho y tế
    medical_intent_patterns = {
        "treatment": ["nên làm gì", "điều trị", "chữa", "xử lý", "uống thuốc gì", "làm sao để", 
                     "cách chữa", "cách điều trị", "cần làm gì", "chữa trị"],
        "prevention": ["phòng ngừa", "tránh", "ngăn ngừa", "cách phòng", "bảo vệ"],
        "symptoms": ["triệu chứng", "dấu hiệu", "biểu hiện", "có triệu chứng gì"],
        "definition": ["là gì", "định nghĩa", "thông tin", "tìm hiểu về"],
        "vaccine": ["vắc xin", "tiêm chủng", "vaccine"],
        "emergency": ["cấp cứu", "khẩn cấp", "nguy hiểm", "nghiêm trọng"]
    }
    
    detected_intents = []
    for intent, patterns in medical_intent_patterns.items():
        for pattern in patterns:
            if pattern in user_input_lower:
                detected_intents.append(intent)
                break
    
    # Ưu tiên intent
    priority_order = ["emergency", "symptom_analysis", "treatment", "symptoms", "prevention", "vaccine", "definition"]
    
    for intent in priority_order:
        if intent in detected_intents:
            return intent
    
    return "general"


def extract_symptoms_from_input(user_input):
    """Trích xuất triệu chứng từ ngôn ngữ tự nhiên"""
    user_input_lower = user_input.lower()
    
    # Dictionary mapping triệu chứng với các từ khóa
    symptom_keywords = {
        "ho": ["ho", "ho khan", "ho có đờm", "khạc đờm", "coughing"],
        "sốt": ["sốt", "nóng người", "ớn lạnh", "fever", "bị sốt", "sốt cao"],
        "đau họng": ["đau họng", "rát họng", "khó nuốt", "sore throat", "họng đau"],
        "khó thở": ["khó thở", "thở khó", "ngạt thở", "thở gấp", "difficulty breathing"],
        "mệt mỏi": ["mệt", "mệt mỏi", "kiệt sức", "uể oải", "fatigue", "tired"],
        "đau đầu": ["đau đầu", "nhức đầu", "headache", "đầu đau"],
        "sổ mũi": ["sổ mũi", "chảy nước mũi", "runny nose", "mũi chảy"],
        "nghẹt mũi": ["nghẹt mũi", "tắc mũi", "blocked nose", "mũi bị tắc"],
        "mất vị giác": ["mất vị", "không cảm nhận vị", "loss of taste", "mất vị giác"],
        "mất khứu giác": ["mất mùi", "không ngửi được", "loss of smell", "mất khứu giác"],
        "buồn nôn": ["buồn nôn", "nôn", "nausea", "muốn nôn"],
        "tiêu chảy": ["tiêu chảy", "đi lỏng", "diarrhea", "bụng xoắn"],
        "đau cơ": ["đau cơ", "nhức cơ", "muscle pain", "cơ thể đau"],
        "ngứa": ["ngứa", "ngứa ngáy", "itchy", "swelling"],
        "phát ban": ["phát ban", "nổi mề đay", "rash", "ban đỏ", "mẩn đỏ"],
        "hắt hơi": ["hắt hơi", "sneezing", "hay hắt hơi"]
    }
    
    detected_symptoms = []
    for symptom, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                detected_symptoms.append(symptom)
                break
    
    return detected_symptoms


def analyze_symptoms_to_diseases(symptoms):
    """Phân tích triệu chứng để đưa ra các bệnh có thể"""
    if not symptoms:
        return []
    
    # Mapping triệu chứng với các bệnh và probability
    disease_symptom_mapping = {
        "covid19": {
            "common": ["sốt", "ho", "mệt mỏi", "đau họng", "mất vị giác", "mất khứu giác"],
            "moderate": ["khó thở", "đau đầu", "đau cơ"],
            "severe": ["khó thở", "đau ngực"]
        },
        "flu": {
            "common": ["sốt", "ho", "đau đầu", "mệt mỏi", "đau cơ"],
            "moderate": ["đau họng", "buồn nôn"],
            "severe": ["khó thở"]
        },
        "cold": {
            "common": ["sổ mũi", "nghẹt mũi", "đau họng", "ho"],
            "moderate": ["đau đầu", "mệt mỏi"],
            "severe": []
        },
        "allergy": {
            "common": ["hắt hơi", "ngứa", "sổ mũi", "phát ban"],
            "moderate": ["nghẹt mũi", "khó thở"],
            "severe": ["khó thở"]
        }
    }
    
    disease_scores = {}
    
    for disease, symptom_groups in disease_symptom_mapping.items():
        score = 0
        matched_symptoms = []
        
        for symptom in symptoms:
            if symptom in symptom_groups["common"]:
                score += 3
                matched_symptoms.append(symptom)
            elif symptom in symptom_groups["moderate"]:
                score += 2
                matched_symptoms.append(symptom)
            elif symptom in symptom_groups["severe"]:
                score += 4
                matched_symptoms.append(symptom)
        
        if score > 0:
            disease_scores[disease] = {
                "score": score,
                "matched_symptoms": matched_symptoms,
                "confidence": min(score / 10.0, 0.95)  # Normalize to 0-0.95
            }
    
    # Sắp xếp theo điểm số
    sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1]["score"], reverse=True)
    return sorted_diseases


def detect_disease_from_input(user_input):
    """Phát hiện bệnh từ input người dùng"""
    user_input_lower = user_input.lower()
    
    disease_keywords = {
        "covid19": ["covid", "covid-19", "corona", "coronavirus", "sars-cov-2"],
        "cold": ["cảm lạnh", "cảm cúm", "lạnh", "common cold"],
        "flu": ["cúm", "flu", "influenza", "cúm mùa"],
        "allergy": ["dị ứng", "allergy", "allergic", "phản ứng dị ứng"]
    }
    
    for disease, keywords in disease_keywords.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                return disease
    
    return None


# Ontology-based information extraction với intent awareness
def extract_from_ontology(disease_type, user_input, ontology_data):
    """Trích xuất thông tin từ ontology dựa trên loại bệnh và intent người dùng"""
    if not ontology_data or disease_type not in ontology_data:
        return None, 0
    
    ontology = ontology_data[disease_type]
    user_intent = analyze_user_intent(user_input)
    best_answer = None
    best_score = 0
    
    # Tìm kiếm trong qa_pairs của ontology với ưu tiên theo intent
    if "qa_pairs" in ontology and "categories" in ontology["qa_pairs"]:
        for category_key, category in ontology["qa_pairs"]["categories"].items():
            if "data" in category:
                for item in category["data"]:
                    # Tính điểm dựa trên intent matching
                    intent_bonus = 0
                    question = item.get("question", "").lower()
                    
                    # Áp dụng bonus điểm theo intent
                    if user_intent == "treatment" and any(word in question for word in ["điều trị", "chữa", "làm gì", "xử lý"]):
                        intent_bonus = 0.3
                    elif user_intent == "prevention" and any(word in question for word in ["phòng ngừa", "tránh", "bảo vệ"]):
                        intent_bonus = 0.3
                    elif user_intent == "symptoms" and any(word in question for word in ["triệu chứng", "dấu hiệu"]):
                        intent_bonus = 0.3
                    elif user_intent == "definition" and any(word in question for word in ["là gì", "thông tin"]):
                        intent_bonus = 0.2
                    elif user_intent == "vaccine" and any(word in question for word in ["vắc xin", "tiêm"]):
                        intent_bonus = 0.3
                    
                    # Kiểm tra similarity với question
                    question_score = similarity(user_input, item.get("question", "")) + intent_bonus
                    if question_score > best_score:
                        best_score = question_score
                        best_answer = item
                    
                    # Kiểm tra keywords với intent bonus
                    keywords = item.get("keywords", [])
                    for keyword in keywords:
                        if keyword.lower() in user_input.lower():
                            keyword_score = (similarity(user_input, keyword) * 0.9) + intent_bonus
                            if keyword_score > best_score:
                                best_score = keyword_score
                                best_answer = item
    
    return best_answer, best_score


def get_ontology_symptom_analysis(disease_type, symptoms, ontology_data):
    """Phân tích triệu chứng dựa trên ontology"""
    if not ontology_data or disease_type not in ontology_data:
        return {}
    
    ontology = ontology_data[disease_type]
    analysis = {}
    
    # Trích xuất thông tin triệu chứng từ ontology instances
    if "ontology" in ontology and "instances" in ontology["ontology"]:
        instances = ontology["ontology"]["instances"]
        
        if "symptoms" in instances:
            ontology_symptoms = instances["symptoms"]
            matched_symptoms = []
            
            for symptom in symptoms:
                for onto_symptom in ontology_symptoms:
                    symptom_name = onto_symptom.get("name", "")
                    if symptom.lower() in symptom_name.lower() or symptom_name.lower() in symptom.lower():
                        matched_symptoms.append({
                            "name": symptom_name,
                            "severity": onto_symptom.get("severity", "Unknown"),
                            "duration": onto_symptom.get("duration", "Unknown"),
                            "description": onto_symptom.get("description", "")
                        })
            
            analysis["matched_symptoms"] = matched_symptoms
        
        # Trích xuất thông tin điều trị
        if "treatments" in instances:
            relevant_treatments = []
            for treatment in instances["treatments"]:
                relevant_treatments.append({
                    "name": treatment.get("name", ""),
                    "type": treatment.get("type", ""),
                    "effectiveness": treatment.get("effectiveness", ""),
                    "description": treatment.get("description", "")
                })
            analysis["treatments"] = relevant_treatments
        
        # Trích xuất thông tin phòng ngừa
        if "preventions" in instances:
            prevention_measures = []
            for prevention in instances["preventions"]:
                prevention_measures.append({
                    "name": prevention.get("name", ""),
                    "type": prevention.get("type", ""),
                    "effectiveness": prevention.get("effectiveness", ""),
                    "description": prevention.get("description", "")
                })
            analysis["preventions"] = prevention_measures
    
    return analysis


def get_emergency_response(disease_type, ontology_data):
    """Lấy thông tin cấp cứu từ ontology"""
    if not ontology_data or disease_type not in ontology_data:
        return None
    
    ontology = ontology_data[disease_type]
    
    if "chatbot_responses" in ontology and "emergency" in ontology["chatbot_responses"]:
        return ontology["chatbot_responses"]["emergency"][0]
    
    return None


def create_social_response(intent, user_input=""):
    """Tạo câu trả lời cho các intent xã giao cơ bản"""
    
    social_responses = {
        "greeting": [
            "Xin chào! 👋 Tôi là trợ lý sức khỏe AI. Tôi có thể giúp bạn tìm hiểu về COVID-19, cảm lạnh, cúm, dị ứng và các vấn đề sức khỏe khác. Bạn cần hỗ trợ gì hôm nay?",
            "Chào bạn! 😊 Rất vui được hỗ trợ bạn về các vấn đề sức khỏe. Bạn có triệu chứng nào cần tư vấn hoặc muốn tìm hiểu về bệnh nào không?",
            "Xin chào! 🏥 Tôi sẵn sàng tư vấn cho bạn về sức khỏe. Hãy chia sẻ triệu chứng hoặc câu hỏi của bạn nhé!"
        ],
        
        "goodbye": [
            "Tạm biệt! 👋 Chúc bạn luôn khỏe mạnh. Nhớ đi khám bác sĩ nếu có triệu chứng bất thường nhé!",
            "Chào tạm biệt! 😊 Hy vọng thông tin tôi cung cấp hữu ích cho bạn. Hãy chăm sóc sức khỏe thật tốt!",
            "Tạm biệt và chúc bạn sức khỏe! 🌟 Hãy quay lại nếu có thêm câu hỏi về sức khỏe."
        ],
        
        "thanks": [
            "Rất vui được giúp đỡ bạn! 😊 Nếu có thêm câu hỏi về sức khỏe, đừng ngần ngại hỏi tôi nhé!",
            "Không có gì! 🤗 Sức khỏe là điều quan trọng nhất. Tôi luôn sẵn sàng hỗ trợ bạn.",
            "Cảm ơn bạn! 💚 Hy vọng thông tin đã giúp ích cho bạn. Chúc bạn sức khỏe!"
        ],
        
        "how_are_you": [
            "Tôi đang hoạt động tốt và sẵn sàng hỗ trợ bạn! 🤖💪 Còn bạn thì sao? Có vấn đề gì về sức khỏe cần tư vấn không?",
            "Tôi khỏe và luôn sẵn sàng giúp đỡ! 😊 Bạn có cảm thấy khỏe mạnh không? Có triệu chứng nào cần quan tâm không?",
            "Cảm ơn bạn hỏi thăm! Tôi hoạt động bình thường. 🌟 Quan trọng hơn là sức khỏe của bạn - bạn có ổn không?"
        ],
        
        "what_can_you_do": [
            "Tôi có thể giúp bạn:\n\n🔍 **Phân tích triệu chứng** - Bạn mô tả triệu chứng, tôi sẽ đưa ra các bệnh có thể\n💊 **Tư vấn điều trị** - Cách xử lý khi mắc bệnh\n🛡️ **Hướng dẫn phòng ngừa** - Cách bảo vệ sức khỏe\n📋 **Thông tin bệnh** - Giải thích về COVID-19, cúm, cảm lạnh, dị ứng\n🚨 **Cảnh báo khẩn cấp** - Nhận biết khi cần đi bác sĩ ngay\n\nHãy thử nói 'Tôi bị ho và sốt' hoặc hỏi 'Cách phòng ngừa COVID-19'!",
            "Tôi chuyên hỗ trợ về sức khỏe! 🏥\n\n✨ **Chức năng chính:**\n- Phân tích triệu chứng thông minh\n- Tư vấn điều trị cơ bản\n- Hướng dẫn phòng ngừa bệnh\n- Thông tin về COVID-19, cúm, cảm lạnh, dị ứng\n- Cảnh báo tình huống khẩn cấp\n\nVí dụ: Hãy thử hỏi 'Triệu chứng COVID-19' hoặc 'Tôi bị đau họng'!"
        ],
        
        "ask_more": [
            "Tất nhiên! Tôi luôn sẵn sàng trả lời thêm câu hỏi. 😊\n\n🤔 Bạn có thể hỏi về:\n- Triệu chứng bạn đang gặp phải\n- Cách điều trị các bệnh thường gặp\n- Biện pháp phòng ngừa\n- Thông tin về vắc xin\n- Khi nào cần đi khám bác sĩ\n\nBạn muốn hỏi gì tiếp theo?",
            "Dĩ nhiên rồi! 🌟 Sức khỏe là chủ đề rộng lớn, tôi có thể giúp bạn nhiều việc:\n\n💭 **Gợi ý câu hỏi:**\n- 'Cách phân biệt cúm và cảm lạnh'\n- 'Tôi bị ngứa và nổi mẩn đỏ'\n- 'Vắc xin COVID-19 có an toàn không'\n- 'Dấu hiệu cần cấp cứu'\n\nBạn quan tâm đến vấn đề nào?"
        ],
        
        "compliment": [
            "Cảm ơn bạn! 😊 Tôi cố gắng cung cấp thông tin chính xác nhất để hỗ trợ sức khỏe của bạn. Bạn có câu hỏi nào khác không?",
            "Rất vui khi được khen! 🌟 Mục tiêu của tôi là giúp bạn chăm sóc sức khỏe tốt hơn. Còn gì khác tôi có thể giúp được không?",
            "Cảm ơn lời khen! 💚 Sứ mệnh của tôi là hỗ trợ mọi người về sức khỏe. Bạn cần tư vấn thêm gì nữa không?"
        ],
        
        "help": [
            "Tôi sẵn sàng giúp đỡ! 🆘\n\n📝 **Cách sử dụng:**\n1. **Mô tả triệu chứng:** 'Tôi bị ho và sốt'\n2. **Hỏi về bệnh:** 'COVID-19 là gì?'\n3. **Tư vấn điều trị:** 'Cảm lạnh nên làm gì?'\n4. **Phòng ngừa:** 'Cách tránh dị ứng'\n\n🎯 **Mẹo:** Hãy mô tả cụ thể triệu chứng để tôi phân tích chính xác hơn!\n\nBạn muốn thử ngay không?",
            "Hướng dẫn sử dụng trợ lý sức khỏe AI: 📖\n\n🗣️ **Bạn có thể:**\n- Kể triệu chứng: 'Mình đau đầu và mệt'\n- Hỏi thông tin: 'Triệu chứng cúm'\n- Xin lời khuyên: 'Nên làm gì khi sốt?'\n- Hỏi phòng ngừa: 'Tránh COVID-19 như thế nào?'\n\n💡 **Lưu ý:** Tôi chỉ tư vấn cơ bản, bạn cần đi bác sĩ để chẩn đoán chính xác!"
        ]
    }
    
    if intent in social_responses:
        responses = social_responses[intent]
        # Chọn random một câu trả lời để đa dạng
        import random
        selected_response = random.choice(responses)
        
        return {
            "question": "",  # Không cần tiêu đề cho social responses
            "answer": selected_response
        }
    
    return None


def create_symptom_analysis_response(user_input, ontology_data):
    """Tạo câu trả lời thông minh dựa trên phân tích triệu chứng"""
    
    # Trích xuất triệu chứng từ input
    symptoms = extract_symptoms_from_input(user_input)
    
    if not symptoms:
        return None
    
    # Phân tích triệu chứng để tìm bệnh có thể
    possible_diseases = analyze_symptoms_to_diseases(symptoms)
    
    if not possible_diseases:
        return None
    
    disease_name_map = {
        "covid19": "COVID-19",
        "cold": "cảm lạnh", 
        "flu": "cúm",
        "allergy": "dị ứng"
    }
    
    # Tạo câu trả lời
    symptoms_text = ", ".join(symptoms)
    response = f"Dựa trên các triệu chứng **{symptoms_text}** mà bạn mô tả, có thể bạn đang gặp phải:\n\n"
    
    # Hiển thị các bệnh có thể theo thứ tự confidence
    for i, (disease, info) in enumerate(possible_diseases[:3], 1):  # Top 3 diseases
        disease_name = disease_name_map.get(disease, disease)
        confidence_percent = int(info["confidence"] * 100)
        
        response += f"**{i}. {disease_name}** (khả năng: {confidence_percent}%)\n"
        response += f"   - Triệu chứng khớp: {', '.join(info['matched_symptoms'])}\n"
        
        # Lấy thông tin điều trị từ ontology
        if ontology_data and disease in ontology_data:
            ontology = ontology_data[disease]
            if "ontology" in ontology and "instances" in ontology["ontology"]:
                instances = ontology["ontology"]["instances"]
                
                # Điều trị
                if "treatments" in instances and instances["treatments"]:
                    treatments = instances["treatments"][:2]  # Top 2 treatments
                    treatment_names = []
                    for treatment in treatments:
                        name = treatment.get('name', '')
                        if treatment.get('effectiveness'):
                            eff_map = {"High": "hiệu quả cao", "Medium": "hiệu quả trung bình", "Low": "hiệu quả thấp"}
                            name += f" ({eff_map.get(treatment['effectiveness'], treatment['effectiveness'])})"
                        treatment_names.append(name)
                    response += f"   - Điều trị: {', '.join(treatment_names)}\n"
                
                # Phòng ngừa
                if "preventions" in instances and instances["preventions"]:
                    preventions = instances["preventions"][:2]  # Top 2 preventions
                    prevention_names = [p.get('name', '') for p in preventions]
                    response += f"   - Phòng ngừa: {', '.join(prevention_names)}\n"
        
        response += "\n"
    
    # Lời khuyên chung
    response += "**💡 Lời khuyên:**\n"
    if any(disease == "covid19" for disease, _ in possible_diseases):
        response += "- Nên làm xét nghiệm COVID-19 để chẩn đoán chính xác\n"
    
    if any(symptom in ["khó thở", "sốt cao", "đau ngực"] for symptom in symptoms):
        response += "- ⚠️ **Cần đi khám bác sĩ ngay** do có triệu chứng nghiêm trọng\n"
    else:
        response += "- Nghỉ ngơi, uống nhiều nước và theo dõi triệu chứng\n"
        response += "- Nếu triệu chứng nặng hơn hoặc kéo dài, hãy đi khám bác sĩ\n"
    
    return {
        "question": "",  # Không cần tiêu đề, nội dung đã rõ ràng
        "answer": response
    }


def create_intent_based_response(disease_type, user_intent, ontology_data, detected_symptoms=[]):
    """Tạo câu trả lời dựa trên intent cụ thể"""
    if not ontology_data or disease_type not in ontology_data:
        return None
    
    ontology = ontology_data[disease_type]
    disease_name_map = {
        "covid19": "COVID-19",
        "cold": "cảm lạnh", 
        "flu": "cúm",
        "allergy": "dị ứng"
    }
    disease_name = disease_name_map.get(disease_type, disease_type)
    
    if user_intent == "treatment":
        response = f"**💊 Cách điều trị {disease_name}:**\n\n"
        
        # Lấy thông tin điều trị từ ontology instances
        if "ontology" in ontology and "instances" in ontology["ontology"]:
            instances = ontology["ontology"]["instances"]
            if "treatments" in instances:
                treatments = instances["treatments"][:3]  # Top 3 treatments
                for i, treatment in enumerate(treatments, 1):
                    response += f"{i}. **{treatment.get('name', '')}**"
                    if treatment.get('type'):
                        response += f" ({treatment['type']})"
                    if treatment.get('effectiveness'):
                        eff_map = {"High": "hiệu quả cao", "Medium": "hiệu quả trung bình", "Low": "hiệu quả thấp"}
                        response += f" - {eff_map.get(treatment['effectiveness'], treatment['effectiveness'])}"
                    if treatment.get('description'):
                        response += f"\n   {treatment['description']}"
                    response += "\n\n"
        
        return {"question": "", "answer": response.strip()}
    
    elif user_intent == "prevention":
        response = f"**🛡️ Cách phòng ngừa {disease_name}:**\n\n"
        
        # Lấy thông tin phòng ngừa từ ontology instances
        if "ontology" in ontology and "instances" in ontology["ontology"]:
            instances = ontology["ontology"]["instances"]
            if "preventions" in instances:
                preventions = instances["preventions"][:3]  # Top 3 preventions
                for i, prevention in enumerate(preventions, 1):
                    response += f"{i}. **{prevention.get('name', '')}**"
                    if prevention.get('effectiveness'):
                        eff_map = {"High": "rất hiệu quả", "Medium": "hiệu quả", "Low": "hiệu quả hạn chế"}
                        response += f" - {eff_map.get(prevention['effectiveness'], prevention['effectiveness'])}"
                    if prevention.get('description'):
                        response += f"\n   {prevention['description']}"
                    response += "\n\n"
        
        return {"question": "", "answer": response.strip()}
    
    elif user_intent == "symptoms":
        response = f"**📋 Triệu chứng {disease_name}:**\n\n"
        
        # Lấy thông tin triệu chứng từ ontology instances
        if "ontology" in ontology and "instances" in ontology["ontology"]:
            instances = ontology["ontology"]["instances"]
            if "symptoms" in instances:
                symptoms = instances["symptoms"][:5]  # Top 5 symptoms
                for i, symptom in enumerate(symptoms, 1):
                    response += f"{i}. **{symptom.get('name', '')}**"
                    if symptom.get('severity'):
                        response += f" (mức độ: {symptom['severity']})"
                    if symptom.get('duration'):
                        response += f" - thời gian: {symptom['duration']}"
                    response += "\n"
        
        return {"question": "", "answer": response.strip()}
    
    return None


# Check for emergency keywords
def is_emergency(text):
    emergency_keywords = [
        "khó thở nghiêm trọng", "đau ngực", "lú lẫn", "môi xanh",
        "mất ý thức", "cấp cứu", "nguy kịch", "nghiêm trọng"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in emergency_keywords)


# COVID-19 symptom analysis
def analyze_covid_symptoms(text):
    symptoms = {
        "sốt": ["sốt", "nóng người", "ớn lạnh"],
        "ho": ["ho", "ho khan", "ho có đờm"],
        "đau họng": ["đau họng", "rát họng", "khó nuốt"],
        "khó thở": ["khó thở", "thở khó", "ngạt thở"],
        "mệt mỏi": ["mệt", "mệt mỏi", "kiệt sức"],
        "đau đầu": ["đau đầu", "nhức đầu"],
        "mất vị giác": ["mất vị", "không cảm nhận vị"],
        "mất khứu giác": ["mất mùi", "không ngửi được"]
    }

    detected_symptoms = []
    text_lower = text.lower()

    for symptom, keywords in symptoms.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_symptoms.append(symptom)

    return detected_symptoms


# Risk assessment based on symptoms
def assess_covid_risk(symptoms):
    if not symptoms:
        return "thấp", 0.2

    high_risk_symptoms = ["khó thở", "đau ngực", "sốt cao"]
    medium_risk_symptoms = ["sốt", "ho", "đau họng"]

    risk_score = 0
    for symptom in symptoms:
        if any(hrs in symptom for hrs in high_risk_symptoms):
            risk_score += 0.4
        elif any(mrs in symptom for mrs in medium_risk_symptoms):
            risk_score += 0.2
        else:
            risk_score += 0.1

    if risk_score >= 0.6:
        return "cao", min(risk_score, 0.95)
    elif risk_score >= 0.3:
        return "trung bình", risk_score
    else:
        return "thấp", risk_score


def format_allergy_info(info, specific_symptom=None):
    if isinstance(info, dict):
        if 'common_symptoms' in info:
            formatted = ""
            if specific_symptom:
                # Tách triệu chứng thành các từ riêng lẻ
                symptom_words = specific_symptom.lower().split()
                found_system = None
                found_symptoms = []
                related_symptoms = []

                # Tìm kiếm trong các hệ thống
                for system in info['common_symptoms']:
                    for symptom in system['symptoms']:
                        symptom_lower = symptom.lower()
                        # Kiểm tra xem có từ khóa nào trong triệu chứng cụ thể khớp với triệu chứng trong hệ thống không
                        if any(word in symptom_lower for word in symptom_words):
                            found_system = system
                            found_symptoms.append(symptom)
                        elif any(word in symptom_lower for word in symptom_words):
                            related_symptoms.append(symptom)

                if found_system:
                    formatted += f"**Triệu chứng '{specific_symptom}' có thể liên quan đến hệ thống {found_system['system']}:**\n\n"
                    
                    # Thêm thông tin về triệu chứng chính
                    formatted += "**Triệu chứng chính:**\n"
                    for symptom in found_symptoms:
                        formatted += f"- {symptom}\n"
                    formatted += "\n"

                    # Thêm thông tin về các triệu chứng liên quan
                    if related_symptoms:
                        formatted += "**Các triệu chứng liên quan có thể gặp:**\n"
                        for symptom in related_symptoms:
                            formatted += f"- {symptom}\n"
                        formatted += "\n"

                    # Thêm thông tin về các triệu chứng khác của hệ thống
                    formatted += f"**Các triệu chứng khác của hệ thống {found_system['system']}:**\n"
                    for symptom in found_system['symptoms']:
                        if symptom not in found_symptoms and symptom not in related_symptoms:
                            formatted += f"- {symptom}\n"
                    formatted += "\n"

                    # Thêm thông tin về điều trị nếu có
                    if 'approaches' in info.get('treatment', {}):
                        formatted += "**Các phương pháp điều trị có thể áp dụng:**\n"
                        for approach in info['treatment']['approaches']:
                            formatted += f"- {approach['method']}: {approach['description']}\n"
                else:
                    formatted = f"Không tìm thấy thông tin cụ thể về triệu chứng '{specific_symptom}'. "
                    formatted += "Dưới đây là các triệu chứng dị ứng phổ biến:\n\n"
                    for system in info['common_symptoms']:
                        formatted += f"**{system['system']}:**\n"
                        for symptom in system['symptoms']:
                            formatted += f"- {symptom}\n"
                        formatted += "\n"
            else:
                formatted = "**Triệu chứng dị ứng theo hệ thống:**\n\n"
                for system in info['common_symptoms']:
                    formatted += f"**{system['system']}:**\n"
                    for symptom in system['symptoms']:
                        formatted += f"- {symptom}\n"
                    formatted += "\n"
            
            if 'note' in info:
                formatted += f"*Lưu ý: {info['note']}*\n"
            return formatted
    return str(info)

def format_flu_info(info):
    if isinstance(info, dict):
        formatted = ""
        if 'common_symptoms' in info:
            formatted += "**Triệu chứng phổ biến:**\n"
            for symptom in info['common_symptoms']:
                formatted += f"- {symptom}\n"
            formatted += "\n"
        if 'less_common_symptoms' in info:
            formatted += "**Triệu chứng ít gặp hơn:**\n"
            for symptom in info['less_common_symptoms']:
                formatted += f"- {symptom}\n"
            formatted += "\n"
        if 'duration' in info:
            formatted += f"**Thời gian bệnh:** {info['duration']}\n\n"
        if 'distinction_from_common_cold' in info:
            formatted += f"**Phân biệt với cảm lạnh:** {info['distinction_from_common_cold']}\n"
        return formatted
    return str(info)

def format_cold_info(info):
    if isinstance(info, dict):
        formatted = ""
        if 'definition' in info:
            formatted += f"{info['definition']}\n\n"
        if 'symptoms' in info:
            formatted += "**Triệu chứng:**\n"
            for symptom in info['symptoms']:
                formatted += f"- {symptom}\n"
            formatted += "\n"
        if 'treatment' in info:
            formatted += "**Điều trị:**\n"
            for treatment in info['treatment']:
                formatted += f"- {treatment}\n"
        return formatted
    return str(info)

def format_covid_info(info):
    if isinstance(info, dict):
        formatted = ""
        if 'question' in info and 'answer' in info:
            formatted += f"{info['answer']}\n"
        return formatted
    return str(info)

# Find best matching answer from knowledge base
def find_best_answer(user_input, kb, ontology_data=None):
    if not kb:
        return None, None, []

    best_match = None
    best_score = 0
    matched_disease = None
    detected_symptoms = []

    # Kiểm tra xem có phải câu hỏi về triệu chứng cụ thể không
    symptom_keywords = ["bị", "có", "triệu chứng", "dấu hiệu", "biểu hiện", "đau", "ngứa", "sưng", "nổi", "mẩn", "lạnh", "sốt", "ho"]
    specific_symptom = None
    
    # Tìm từ khóa triệu chứng trong câu hỏi
    for keyword in symptom_keywords:
        if keyword in user_input.lower():
            # Tách từ sau từ khóa để lấy triệu chứng
            parts = user_input.lower().split(keyword)
            if len(parts) > 1:
                # Lấy phần còn lại của câu làm triệu chứng
                specific_symptom = parts[1].strip()
                # Loại bỏ các từ không cần thiết
                specific_symptom = specific_symptom.replace("là gì", "").replace("?", "").strip()
                break

    # Tìm kiếm trong tất cả các knowledge base
    disease_scores = {}
    disease_matches = {}
    disease_symptoms = {}

    # COVID-19
    if "covid19" in kb:
        covid_score = 0
        covid_match = None
        covid_symptoms = []
        
        covid_categories = kb["covid19"]["categories"]
        for category_key, category in covid_categories.items():
            for item in category["data"]:
                # Check intent matching
                for intent in category.get("intent", []):
                    if intent.lower() in user_input.lower():
                        score = similarity(user_input, intent)
                        if score > covid_score:
                            covid_score = score
                            covid_match = item

                # Check question similarity
                question_score = similarity(user_input, item["question"])
                if question_score > covid_score:
                    covid_score = question_score
                    covid_match = item

                # Check keywords
                for keyword in item.get("keywords", []):
                    if keyword.lower() in user_input.lower():
                        keyword_score = similarity(user_input, keyword) * 0.8
                        if keyword_score > covid_score:
                            covid_score = keyword_score
                            covid_match = item

        # Analyze COVID-19 symptoms
        symptoms = analyze_covid_symptoms(user_input)
        if symptoms:
            covid_symptoms = symptoms
            covid_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["covid19"] = covid_score
        disease_matches["covid19"] = covid_match
        disease_symptoms["covid19"] = covid_symptoms

    # Cold
    if "cold" in kb:
        cold_score = 0
        cold_match = None
        cold_symptoms = []
        
        for intent_type, intents in kb["cold"]["chatbot_intents"].items():
            for intent in intents:
                if intent.lower() in user_input.lower():
                    for category_key, category in kb["cold"]["categories"].items():
                        if intent_type in category_key:
                            response = {
                                "question": f"Thông tin về {intent_type} của bệnh cảm lạnh",
                                "answer": format_cold_info(category)
                            }
                            score = similarity(user_input, intent)
                            if score > cold_score:
                                cold_score = score
                                cold_match = response

        # Analyze cold symptoms
        cold_symptom_list = ["sổ mũi", "nghẹt mũi", "đau họng", "ho", "hắt hơi", "đau đầu nhẹ", "sốt nhẹ", "lạnh", "ớn lạnh"]
        for symptom in cold_symptom_list:
            if symptom in user_input.lower():
                cold_symptoms.append(symptom)
                cold_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["cold"] = cold_score
        disease_matches["cold"] = cold_match
        disease_symptoms["cold"] = cold_symptoms

    # Flu
    if "flu" in kb:
        flu_score = 0
        flu_match = None
        flu_symptoms = []
        
        for topic in kb["flu"]["topics"]:
            # Check topic name
            topic_score = similarity(user_input, topic["name"])
            if topic_score > flu_score:
                flu_score = topic_score
                flu_match = {
                    "question": topic["name"],
                    "answer": format_flu_info(topic["information"])
                }

            # Check information content
            if isinstance(topic["information"], dict):
                for key, value in topic["information"].items():
                    if isinstance(value, str):
                        content_score = similarity(user_input, value)
                        if content_score > flu_score:
                            flu_score = content_score
                            flu_match = {
                                "question": topic["name"],
                                "answer": format_flu_info(topic["information"])
                            }

        # Analyze flu symptoms
        flu_symptom_list = ["sốt cao", "ớn lạnh", "đau cơ", "mệt mỏi", "ho", "đau họng", "đau đầu", "sổ mũi", "lạnh"]
        for symptom in flu_symptom_list:
            if symptom in user_input.lower():
                flu_symptoms.append(symptom)
                flu_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["flu"] = flu_score
        disease_matches["flu"] = flu_match
        disease_symptoms["flu"] = flu_symptoms

    # Allergy
    if "allergy" in kb:
        allergy_score = 0
        allergy_match = None
        allergy_symptoms = []
        
        for topic in kb["allergy"]["topics"]:
            # Check topic name
            topic_score = similarity(user_input, topic["name"])
            if topic_score > allergy_score:
                allergy_score = topic_score
                allergy_match = {
                    "question": topic["name"],
                    "answer": format_allergy_info(topic["information"], specific_symptom)
                }

            # Check information content
            if isinstance(topic["information"], dict):
                for key, value in topic["information"].items():
                    if isinstance(value, str):
                        content_score = similarity(user_input, value)
                        if content_score > allergy_score:
                            allergy_score = content_score
                            allergy_match = {
                                "question": topic["name"],
                                "answer": format_allergy_info(topic["information"], specific_symptom)
                            }

        # Analyze allergy symptoms
        allergy_symptom_list = ["hắt hơi", "ngứa mũi", "chảy nước mũi", "ngứa mắt", "phát ban", "nổi mề đay", "ngứa da", "ngứa", "mẩn ngứa", "nổi mụn nước", "bong tróc da", "chàm"]
        for symptom in allergy_symptom_list:
            if symptom in user_input.lower():
                allergy_symptoms.append(symptom)
                allergy_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["allergy"] = allergy_score
        disease_matches["allergy"] = allergy_match
        disease_symptoms["allergy"] = allergy_symptoms

    # Tìm bệnh có điểm cao nhất từ knowledge base
    best_disease = max(disease_scores.items(), key=lambda x: x[1])
    kb_best_match = None
    kb_best_disease = None
    kb_symptoms = []
    
    if best_disease[1] > 0.3:
        kb_best_match = disease_matches[best_disease[0]]
        kb_best_disease = best_disease[0]
        kb_symptoms = disease_symptoms[best_disease[0]]
    
    # Tích hợp kết quả từ ontology nếu có
    ontology_best_match = None
    ontology_best_score = 0
    ontology_disease = None
    
    if ontology_data:
        user_intent = analyze_user_intent(user_input)
        detected_disease = detect_disease_from_input(user_input)
        
        # Ưu tiên cao nhất: Social responses (chào hỏi, cảm ơn, etc.)
        social_intents = ["greeting", "goodbye", "thanks", "how_are_you", "what_can_you_do", 
                         "ask_more", "compliment", "help"]
        
        if user_intent in social_intents:
            social_response = create_social_response(user_intent, user_input)
            if social_response:
                ontology_best_match = social_response
                ontology_best_score = 0.99  # Score cao nhất để ưu tiên social responses
                ontology_disease = "social"
        
        # Ưu tiên thứ 2: Phân tích triệu chứng từ ngôn ngữ tự nhiên
        if not ontology_best_match and user_intent == "symptom_analysis":
            symptom_response = create_symptom_analysis_response(user_input, ontology_data)
            if symptom_response:
                ontology_best_match = symptom_response
                ontology_best_score = 0.98  # Score rất cao để ưu tiên symptom analysis
                ontology_disease = "symptom_analysis"
        
        # Nếu có intent rõ ràng và detect được disease, tạo câu trả lời trực tiếp
        if not ontology_best_match:
            target_disease = detected_disease if detected_disease else (best_disease[0] if best_disease[1] > 0.2 else None)
            
            if user_intent in ["treatment", "prevention", "symptoms"] and target_disease:
                intent_response = create_intent_based_response(target_disease, user_intent, ontology_data, disease_symptoms.get(target_disease, []))
                if intent_response:
                    ontology_best_match = intent_response
                    ontology_best_score = 0.95  # Score cao để ưu tiên intent-based response
                    ontology_disease = target_disease
        
        # Fallback: Tìm kiếm trong tất cả các ontology như cũ
        if not ontology_best_match:
            for disease_type in ["covid19", "cold", "flu", "allergy"]:
                onto_answer, onto_score = extract_from_ontology(disease_type, user_input, ontology_data)
                if onto_answer and onto_score > ontology_best_score:
                    ontology_best_score = onto_score
                    ontology_best_match = onto_answer
                    ontology_disease = disease_type
    
    # Quyết định kết quả tốt nhất
    if ontology_best_score > best_disease[1] and ontology_best_score > 0.3:
        # Ontology có kết quả tốt hơn
        return ontology_best_match, ontology_disease, []
    elif kb_best_match:
        # Knowledge base có kết quả tốt hơn hoặc bằng
        return kb_best_match, kb_best_disease, kb_symptoms
    elif ontology_best_match and ontology_best_score > 0.2:
        # Dùng ontology như backup nếu KB không có kết quả tốt
        return ontology_best_match, ontology_disease, []
    
    return None, None, []


# Generate COVID-19 specific recommendations
def generate_covid_recommendations(symptoms, risk_level):
    base_recommendations = [
        "🏠 Cách ly tại nhà ít nhất 5 ngày",
        "😷 Đeo khẩu trang khi tiếp xúc với người khác",
        "🚰 Uống nhiều nước, nghỉ ngơi đầy đủ",
        "🌡️ Theo dõi thân nhiệt thường xuyên"
    ]

    if risk_level == "cao":
        base_recommendations.extend([
            "🏥 Liên hệ bác sĩ ngay lập tức",
            "📞 Gọi hotline COVID-19: 19009095",
            "⚠️ Đến bệnh viện nếu khó thở tăng"
        ])
    elif risk_level == "trung bình":
        base_recommendations.extend([
            "📞 Liên hệ trạm y tế địa phương",
            "🧪 Xem xét làm xét nghiệm COVID-19"
        ])

    return base_recommendations


# Main UI
def main():
    st.title("🏥 Hệ thống Tư vấn Sức khỏe AI")
    st.markdown("💬 **Hỏi đáp thông tin về các bệnh thường gặp với AI**")

    # Load knowledge base và ontology
    kb = load_knowledge_base()
    ontology_data = load_ontology_data()
    
    if not kb:
        st.stop()
    
    # Hiển thị trạng thái hệ thống (chỉ cho developer, ẩn khỏi người dùng cuối)
    if ontology_data:
        st.success("✅ Hệ thống AI đã sẵn sàng với đầy đủ tính năng!")
    else:
        st.warning("⚠️ Đang chạy ở chế độ cơ bản. Một số tính năng nâng cao có thể không khả dụng.")

    # Sidebar with quick info
    with st.sidebar:
        st.header("📋 Thông tin nhanh")
        st.markdown("""
        **Hotline khẩn cấp:**
        - 🚨 Cấp cứu: **115**
        - 📞 COVID-19: **19009095**
        - 🏥 Bộ Y tế: **19003228**

        **Triệu chứng cần cấp cứu:**
        - Khó thở nghiêm trọng
        - Đau ngực dai dẳng
        - Môi xanh tím
        - Lú lẫn, mất ý thức
        - Sốc phản vệ (dị ứng)
        - Sốt cao kéo dài
        """)

        st.markdown("---")
        st.markdown("**Phòng ngừa cơ bản:**")
        st.markdown("- 😷 Đeo khẩu trang khi cần")
        st.markdown("- 🧼 Rửa tay thường xuyên")
        st.markdown("- 📏 Giữ khoảng cách an toàn")
        st.markdown("- 💉 Tiêm vắc xin đầy đủ")
        st.markdown("- 🏠 Giữ ấm cơ thể")
        st.markdown("- 🥗 Ăn uống đầy đủ dinh dưỡng")
        st.markdown("- 🌿 Tránh các tác nhân gây dị ứng")
        
        st.markdown("---")
        st.markdown("**Hệ thống hỗ trợ:**")
        if ontology_data:
            st.markdown("- 🧠 **AI nâng cao** - Phân tích chuyên sâu")
            st.markdown("- 📚 **Cơ sở dữ liệu** - Thông tin y tế")
            st.markdown("- 🔍 **Tìm kiếm thông minh** - Kết quả chính xác")
        else:
            st.markdown("- 📚 **Cơ sở dữ liệu** - Thông tin y tế")
            st.markdown("- ⚠️ **AI nâng cao** - Đang tải...")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Add welcome message
        welcome_msg = "Xin chào! 👋 Tôi là trợ lý sức khỏe AI thông minh.\n\n🔍 **Tôi có thể giúp bạn:**\n- Phân tích triệu chứng (VD: 'Tôi bị ho và sốt')\n- Tư vấn điều trị các bệnh thường gặp\n- Hướng dẫn phòng ngừa COVID-19, cúm, cảm lạnh, dị ứng\n- Cảnh báo khi cần đi bác sĩ ngay\n\n💬 Hãy mô tả triệu chứng hoặc hỏi câu hỏi của bạn!"
        st.session_state.chat_history.append(("AI", welcome_msg))

    # Clear chat button
    if st.button("🗑️ Xóa cuộc trò chuyện"):
        # Xóa lịch sử chat
        st.session_state.chat_history = []
        # Thêm lại tin nhắn chào mừng
        welcome_msg = "Xin chào! 👋 Tôi là trợ lý sức khỏe AI thông minh.\n\n🔍 **Tôi có thể giúp bạn:**\n- Phân tích triệu chứng (VD: 'Tôi bị ho và sốt')\n- Tư vấn điều trị các bệnh thường gặp\n- Hướng dẫn phòng ngừa COVID-19, cúm, cảm lạnh, dị ứng\n- Cảnh báo khi cần đi bác sĩ ngay\n\n💬 Hãy mô tả triệu chứng hoặc hỏi câu hỏi của bạn!"
        st.session_state.chat_history.append(("AI", welcome_msg))
        # Xóa input của người dùng
        st.session_state.user_input = ""
        # Làm mới trang
        st.rerun()

    # Chat input
    user_input = st.text_input("💭 Bạn muốn hỏi gì về sức khỏe?", key="user_input")

    # Process user input
    if user_input:
        # Add user message to chat
        st.session_state.chat_history.append(("User", user_input))

        # Check for emergency
        if is_emergency(user_input):
            # Lấy thông tin cấp cứu từ ontology nếu có
            emergency_response = "⚠️ **CẢNH BÁO KHẨN CẤP!**\n\nVui lòng gọi ngay số cấp cứu 115 hoặc đến bệnh viện gần nhất nếu bạn đang gặp các triệu chứng nghiêm trọng như khó thở, đau ngực, môi xanh tím, hoặc mất ý thức."
            
            # Thêm thông tin cấp cứu từ ontology
            if ontology_data:
                for disease_type in ["covid19", "cold", "flu", "allergy"]:
                    emergency_onto = get_emergency_response(disease_type, ontology_data)
                    if emergency_onto:
                        emergency_response += f"\n\n{emergency_onto}"
                        break
            
            st.session_state.chat_history.append(("AI", emergency_response))
        else:
            # Find answer from knowledge base và ontology
            answer, matched_disease, detected_symptoms = find_best_answer(user_input, kb, ontology_data)

            if answer:
                response = f"**📋 {answer['question']}**\n\n{answer['answer']}"

                # Add disease-specific analysis if symptoms detected
                if detected_symptoms:
                    if matched_disease == "covid19":
                        risk_level, confidence = assess_covid_risk(detected_symptoms)
                        response += f"\n\n**🔍 Phân tích triệu chứng COVID-19:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Mức độ nguy cơ: **{risk_level}** ({int(confidence * 100)}%)"

                        # Add COVID-19 recommendations
                        recommendations = generate_covid_recommendations(detected_symptoms, risk_level)
                        response += f"\n\n**💊 Khuyến nghị cho COVID-19:**"
                        for rec in recommendations:
                            response += f"\n{rec}"
                    elif matched_disease == "cold":
                        response += f"\n\n**🔍 Phân tích triệu chứng cảm lạnh:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Khuyến nghị: Nghỉ ngơi, uống nhiều nước, giữ ấm cơ thể"
                    elif matched_disease == "flu":
                        response += f"\n\n**🔍 Phân tích triệu chứng cúm:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Khuyến nghị: Nghỉ ngơi, uống nhiều nước, dùng thuốc hạ sốt nếu cần"
                    elif matched_disease == "allergy":
                        response += f"\n\n**🔍 Phân tích triệu chứng dị ứng:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Khuyến nghị: Tránh tiếp xúc với tác nhân gây dị ứng, dùng thuốc kháng histamine nếu cần"
                
                # Thêm thông tin từ ontology một cách tự nhiên (chỉ khi không phải symptom analysis hoặc social)
                if ontology_data and matched_disease and matched_disease not in ["symptom_analysis", "social"]:
                    ontology_analysis = get_ontology_symptom_analysis(matched_disease, detected_symptoms, ontology_data)
                    
                    if ontology_analysis:
                        # Tích hợp thông tin điều trị từ ontology
                        if "treatments" in ontology_analysis and ontology_analysis["treatments"]:
                            treatment_info = []
                            for treatment in ontology_analysis["treatments"][:2]:  # Chỉ lấy 2 phương pháp hàng đầu
                                if treatment['effectiveness'] and treatment['effectiveness'] != "":
                                    effectiveness_map = {"High": "cao", "Medium": "trung bình", "Low": "thấp"}
                                    eff_text = effectiveness_map.get(treatment['effectiveness'], treatment['effectiveness'])
                                    treatment_info.append(f"{treatment['name']} (hiệu quả {eff_text})")
                                else:
                                    treatment_info.append(treatment['name'])
                            
                            if treatment_info:
                                response += f"\n\n**💊 Các phương pháp điều trị khuyến nghị:** {', '.join(treatment_info)}."
                        
                        # Tích hợp thông tin phòng ngừa từ ontology
                        if "preventions" in ontology_analysis and ontology_analysis["preventions"]:
                            prevention_info = []
                            for prevention in ontology_analysis["preventions"][:2]:  # Chỉ lấy 2 biện pháp hàng đầu
                                if prevention['effectiveness'] and prevention['effectiveness'] != "":
                                    effectiveness_map = {"High": "rất hiệu quả", "Medium": "hiệu quả", "Low": "hiệu quả hạn chế"}
                                    eff_text = effectiveness_map.get(prevention['effectiveness'], prevention['effectiveness'])
                                    prevention_info.append(f"{prevention['name']} ({eff_text})")
                                else:
                                    prevention_info.append(prevention['name'])
                            
                            if prevention_info:
                                response += f"\n\n**🛡️ Biện pháp phòng ngừa quan trọng:** {', '.join(prevention_info)}."
                        
                        # Hiển thị thông tin triệu chứng chi tiết nếu có
                        if "matched_symptoms" in ontology_analysis and ontology_analysis["matched_symptoms"]:
                            detailed_symptoms = []
                            for symp in ontology_analysis["matched_symptoms"][:2]:  # Chỉ hiển thị 2 triệu chứng chi tiết nhất
                                symptom_detail = symp['name']
                                if symp['duration'] != "Unknown" and symp['duration']:
                                    symptom_detail += f" (thường kéo dài {symp['duration']})"
                                detailed_symptoms.append(symptom_detail)
                            
                            if detailed_symptoms:
                                response += f"\n\n**📋 Thông tin bổ sung về triệu chứng:** {', '.join(detailed_symptoms)}."

                # Add disclaimer (chỉ cho medical responses)
                if matched_disease not in ["social"]:
                    response += f"\n\n⚠️ Lưu ý: Thông tin tôi cung cấp chỉ mang tính chất tham khảo. Để được chẩn đoán và điều trị chính xác, bạn cần tham khảo ý kiến bác sĩ hoặc cơ sở y tế có thẩm quyền."

            else:
                # Fallback response
                response = "Xin lỗi, tôi chưa có đủ thông tin để trả lời câu hỏi của bạn. Vui lòng thử hỏi lại theo cách khác hoặc liên hệ với bác sĩ để được tư vấn chi tiết hơn."

            st.session_state.chat_history.append(("AI", response))

    # Display chat history
    st.markdown("### 💬 Cuộc trò chuyện")
    chat_container = st.container()

    with chat_container:
        for i, (speaker, message) in enumerate(st.session_state.chat_history):
            if speaker == "User":
                st.markdown(
                    f"""
                    <div style="text-align: right; margin: 10px 0;">
                        <div style="display: inline-block; background-color: #007bff; color: white; 
                                    padding: 10px 15px; border-radius: 15px 15px 5px 15px; max-width: 70%;">
                            <strong>👤 Bạn:</strong> {message}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="text-align: left; margin: 10px 0;">
                        <div style="display: inline-block; background-color: #f8f9fa; color: black; 
                                    padding: 10px 15px; border-radius: 15px 15px 15px 5px; max-width: 70%;
                                    border-left: 4px solid #28a745;">
                            <strong>🤖 AI:</strong><br>{message}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Quick action buttons
    st.markdown("### 🚀 Câu hỏi gợi ý")
    
    quick_questions = [
        "Xin chào! 👋",
        "Bạn có thể làm gì?",
        "Tôi bị ho và sốt",
        "Triệu chứng cúm là gì?",
        "Cách phòng ngừa dị ứng?",
        "Điều trị cảm lạnh tại nhà?",
        "COVID-19 là gì?",
        "Cảm ơn bạn! 💚"
    ]

    # Hiển thị câu hỏi theo 2 hàng, mỗi hàng 4 cột
    col1, col2, col3, col4 = st.columns(4)
    cols_row1 = [col1, col2, col3, col4]
    
    for i, question in enumerate(quick_questions[:4]):
        if cols_row1[i].button(question, key=f"quick_{i}"):
            st.session_state.chat_history.append(("User", question))
            st.rerun()
    
    # Hàng thứ 2
    if len(quick_questions) > 4:
        col5, col6, col7, col8 = st.columns(4)
        cols_row2 = [col5, col6, col7, col8]
        
        for i, question in enumerate(quick_questions[4:8]):
            if cols_row2[i].button(question, key=f"quick_{i+4}"):
                st.session_state.chat_history.append(("User", question))
                st.rerun()


if __name__ == "__main__":
    main()