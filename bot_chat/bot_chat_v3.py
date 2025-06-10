import streamlit as st
import json
import random
from typing import Dict, List, Tuple, Optional
import re

# Cấu hình trang
st.set_page_config(
    page_title="Health Assistant",
    page_icon="🏥",
    layout="wide"
)

# Load knowledge base và ontology
def load_knowledge_base() -> Tuple[Dict, Dict, Dict, Dict]:
    with open('data/covid.json', 'r', encoding='utf-8') as f:
        covid_kb = json.load(f)
    with open('data/allergy.json', 'r', encoding='utf-8') as f:
        allergy_kb = json.load(f)
    with open('data/ontology/covid_ontology.json', 'r', encoding='utf-8') as f:
        covid_ontology = json.load(f)
    with open('data/ontology/allergy_ontology.json', 'r', encoding='utf-8') as f:
        allergy_ontology = json.load(f)
    return covid_kb, allergy_kb, covid_ontology, allergy_ontology

# Khởi tạo knowledge base và ontology
covid_kb, allergy_kb, covid_ontology, allergy_ontology = load_knowledge_base()

class OntologyMatcher:
    def __init__(self, ontologies: Dict[str, Dict]):
        self.ontologies = ontologies
        
    def find_related_instances(self, instance_id: str, disease_type: str) -> List[Dict]:
        """Tìm các instance liên quan dựa trên relationships"""
        related = []
        ontology = self.ontologies.get(disease_type, {})
        for instance_type, instances in ontology.get('ontology', {}).get('instances', {}).items():
            for instance in instances:
                if instance_id in instance.get('id', ''):
                    related.append(instance)
        return related
    
    def get_class_properties(self, class_name: str, disease_type: str) -> Dict:
        """Lấy properties của một class"""
        ontology = self.ontologies.get(disease_type, {})
        return ontology.get('ontology', {}).get('classes', {}).get(class_name, {}).get('properties', {})
    
    def find_matching_instances(self, query: str, disease_type: str) -> List[Dict]:
        """Tìm các instance phù hợp với query"""
        matches = []
        query = query.lower()
        ontology = self.ontologies.get(disease_type, {})
        
        for instance_type, instances in ontology.get('ontology', {}).get('instances', {}).items():
            for instance in instances:
                # Kiểm tra tên và các thuộc tính
                if any(query in str(value).lower() for value in instance.values()):
                    matches.append(instance)
        return matches

def detect_disease_type(user_input: str) -> str:
    """
    Xác định loại bệnh từ câu hỏi của người dùng
    """
    covid_keywords = ["covid", "corona", "sars", "virus", "đại dịch"]
    allergy_keywords = ["dị ứng", "allergy", "mề đay", "phát ban", "ngứa"]
    
    user_input = user_input.lower()
    
    covid_score = sum(1 for keyword in covid_keywords if keyword in user_input)
    allergy_score = sum(1 for keyword in allergy_keywords if keyword in user_input)
    
    if covid_score > allergy_score:
        return "covid"
    elif allergy_score > covid_score:
        return "allergy"
    return "general"

def find_best_match(user_input: str, ontology_matcher: OntologyMatcher) -> Tuple[Optional[str], str]:
    """
    Tìm câu trả lời phù hợp nhất cho câu hỏi của người dùng
    """
    # Xác định loại bệnh
    disease_type = detect_disease_type(user_input)
    
    # Chọn knowledge base và ontology tương ứng
    kb = covid_kb if disease_type == "covid" else allergy_kb
    ontology = covid_ontology if disease_type == "covid" else allergy_ontology
    
    best_score = 0
    best_answer = None
    best_category = None
    all_matches = []
    related_info = []
    
    # Chuẩn hóa input
    user_input = user_input.lower()
    
    # Tìm kiếm trong ontology
    ontology_matches = ontology_matcher.find_matching_instances(user_input, disease_type)
    if ontology_matches:
        for match in ontology_matches:
            related = ontology_matcher.find_related_instances(match['id'], disease_type)
            related_info.extend(related)
    
    # Tìm kiếm trong knowledge base
    if disease_type == "covid":
        categories = kb['covid19_knowledge_base']['categories']
    else:
        categories = kb['topics']
    
    for category, data in categories.items():
        # Kiểm tra intent
        if 'intent' in data:
            for intent in data['intent']:
                if intent in user_input:
                    if disease_type == "covid":
                        all_matches.append((data['title'], random.choice(data['data'])['answer']))
                    else:
                        all_matches.append((data['name'], data['information'].get('definition', '')))
        
        # Kiểm tra các câu hỏi và từ khóa
        if disease_type == "covid":
            for qa in data.get('data', []):
                if qa['question'].lower() in user_input:
                    all_matches.append((data['title'], qa['answer']))
                for keyword in qa.get('keywords', []):
                    if keyword in user_input:
                        score = len(keyword) / len(user_input)
                        if score > best_score:
                            best_score = score
                            best_answer = qa['answer']
                            best_category = data['title']
        else:
            # Xử lý cho allergy
            for key, value in data.get('information', {}).items():
                if isinstance(value, str) and any(keyword in value.lower() for keyword in user_input.split()):
                    all_matches.append((data['name'], value))
    
    # Trích xuất triệu chứng
    symptoms = extract_symptoms(user_input, disease_type)
    
    # Nếu tìm thấy nhiều kết quả phù hợp
    if len(all_matches) > 0:
        # Sắp xếp theo độ phù hợp
        all_matches.sort(key=lambda x: len(x[1]), reverse=True)
        # Lấy 5 kết quả phù hợp nhất
        top_matches = all_matches[:5]
        
        # Tìm thông tin liên quan cho danh mục chính
        related_categories = find_related_categories(top_matches[0][0].lower().replace(" ", "_"), user_input, disease_type)
        
        # Tạo câu trả lời tổng hợp
        answer = ""
        for category, match_answer in top_matches:
            answer += format_response(category, match_answer, 
                                   related_info if category == top_matches[0][0] else None,
                                   symptoms if category == top_matches[0][0] else None,
                                   related_categories if category == top_matches[0][0] else None)
        return "Thông tin tổng hợp", answer
    
    # Nếu không tìm thấy kết quả phù hợp
    if best_answer is None:
        if disease_type == "covid":
            return None, random.choice(kb['covid19_knowledge_base']['chatbot_responses']['fallback'])
        else:
            return None, random.choice(kb['chatbot_responses']['fallback'])
    
    # Tìm thông tin liên quan cho danh mục tốt nhất
    related_categories = find_related_categories(best_category.lower().replace(" ", "_"), user_input, disease_type)
    
    return best_category, format_response(best_category, best_answer, related_info, symptoms, related_categories)

def extract_symptoms(user_input: str, disease_type: str) -> List[str]:
    """
    Trích xuất các triệu chứng từ câu hỏi của người dùng
    """
    if disease_type == "covid":
        symptom_keywords = covid_kb['covid19_knowledge_base']['nlp_patterns']['symptom_keywords']
    else:
        # Lấy triệu chứng từ allergy ontology
        symptoms = []
        for instance in allergy_ontology['ontology']['instances'].get('symptoms', []):
            symptoms.extend(instance.get('symptoms', []))
        symptom_keywords = symptoms
    
    return [symptom for symptom in symptom_keywords if symptom in user_input.lower()]

def find_related_categories(category: str, user_input: str, disease_type: str) -> List[Tuple[str, str]]:
    """
    Tìm các danh mục liên quan dựa trên category và user_input
    """
    related = []
    if disease_type == "covid":
        category_mapping = {
            "trieu_chung": ["dieu_tri", "cap_cuu", "xet_nghiem"],
            "vac_xin": ["phong_ngua", "bien_the", "nhom_nguy_co"],
            # ... (các mapping khác cho COVID-19)
        }
    else:
        category_mapping = {
            "tổng_quan_về_dị_ứng": ["nguyên_nhân_gây_dị_ứng", "triệu_chứng_dị_ứng", "chẩn_đoán_dị_ứng"],
            "triệu_chứng_dị_ứng": ["chẩn_đoán_dị_ứng", "điều_trị_và_quản_lý_dị_ứng"],
            # ... (các mapping cho dị ứng)
        }
    
    # Lấy các danh mục liên quan
    related_cats = category_mapping.get(category, [])
    
    # Tìm thông tin từ các danh mục liên quan
    kb = covid_kb if disease_type == "covid" else allergy_kb
    categories = kb['covid19_knowledge_base']['categories'] if disease_type == "covid" else kb['topics']
    
    for cat in related_cats:
        if cat in categories:
            data = categories[cat]
            if disease_type == "covid":
                best_match = None
                for qa in data['data']:
                    if any(keyword in user_input.lower() for keyword in qa['keywords']):
                        best_match = (data['title'], qa['answer'])
                        break
            else:
                best_match = (data['name'], data['information'].get('definition', ''))
            
            if best_match:
                related.append(best_match)
    
    return related

def format_response(category: str, answer: str, related_info: List[Dict] = None, symptoms: List[str] = None, related_categories: List[Tuple[str, str]] = None) -> str:
    """
    Định dạng câu trả lời với cấu trúc rõ ràng và nhiều thông tin liên quan
    """
    response = f"## {category}\n\n"
    
    # Thêm thông tin chính
    response += f"{answer}\n\n"
    
    # Thêm thông tin liên quan từ ontology nếu có
    if related_info:
        response += "### Thông tin bổ sung từ cơ sở dữ liệu y tế:\n"
        for info in related_info:
            response += f"- {info.get('name', '')}: {', '.join(str(v) for v in info.values() if v != info.get('name', ''))}\n"
        response += "\n"
    
    # Thêm thông tin về triệu chứng nếu có
    if symptoms:
        response += "### Triệu chứng được đề cập:\n"
        for symptom in symptoms:
            response += f"- {symptom}\n"
        response += "\n"
    
    # Thêm thông tin từ các danh mục liên quan
    if related_categories:
        response += "### Thông tin liên quan:\n"
        for cat, ans in related_categories:
            response += f"#### {cat}\n{ans}\n\n"
    
    return response

# Khởi tạo OntologyMatcher
ontology_matcher = OntologyMatcher({
    "covid": covid_ontology,
    "allergy": allergy_ontology
})

# UI
st.title("🏥 Health Assistant")
st.write("Xin chào! Tôi là trợ lý ảo y tế. Tôi có thể giúp bạn tìm hiểu về COVID-19 và dị ứng. Bạn cần hỗ trợ thông tin gì?")

# Khởi tạo chat history
if "chat" not in st.session_state:
    st.session_state.chat = []

# Input từ người dùng
user_input = st.text_input("Bạn cần hỗ trợ thông tin gì?", key="input")

if user_input:
    # Thêm câu hỏi vào chat
    st.session_state.chat.append(("Bạn", user_input))
    
    # Kiểm tra tình huống khẩn cấp
    if check_emergency(user_input):
        response = random.choice(covid_kb['covid19_knowledge_base']['chatbot_responses']['emergency'])
        st.session_state.chat.append(("AI", response))
    else:
        # Tìm câu trả lời phù hợp
        category, answer = find_best_match(user_input, ontology_matcher)
        
        if category:
            response = answer
        else:
            response = answer
            
        # Thêm disclaimer
        response += f"\n\n{knowledge_base['covid19_knowledge_base']['chatbot_responses']['disclaimer']}"
        
        st.session_state.chat.append(("AI", response))

# Hiển thị chat history
for speaker, msg in st.session_state.chat:
    if speaker == "Bạn":
        st.markdown(f"**👤 {speaker}:** {msg}")
    else:
        st.markdown(f"**🤖 {speaker}:** {msg}")

# Hiển thị thông tin liên hệ
st.sidebar.title("Thông tin liên hệ khẩn cấp")
st.sidebar.write("🚨 Cấp cứu:", covid_kb['covid19_knowledge_base']['chatbot_responses']['contact_info']['emergency'])
st.sidebar.write("📞 Bộ Y tế:", covid_kb['covid19_knowledge_base']['chatbot_responses']['contact_info']['health_ministry_hotline'])
st.sidebar.write("📞 COVID-19:", covid_kb['covid19_knowledge_base']['chatbot_responses']['contact_info']['covid_hotline'])

# Hiển thị thông tin ontology
st.sidebar.title("Thông tin Ontology")
st.sidebar.write("COVID-19:")
st.sidebar.write("- Số lượng classes:", len(covid_ontology['ontology']['classes']))
st.sidebar.write("- Số lượng relationships:", len(covid_ontology['ontology']['relationships']))
st.sidebar.write("- Số lượng instances:", sum(len(instances) for instances in covid_ontology['ontology']['instances'].values()))

st.sidebar.write("\nDị ứng:")
st.sidebar.write("- Số lượng classes:", len(allergy_ontology['ontology']['classes']))
st.sidebar.write("- Số lượng relationships:", len(allergy_ontology['ontology']['relationships']))
st.sidebar.write("- Số lượng instances:", sum(len(instances) for instances in allergy_ontology['ontology']['instances'].values())) 