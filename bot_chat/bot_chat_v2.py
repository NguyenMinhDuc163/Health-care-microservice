import streamlit as st
import json
import random
from typing import Dict, List, Tuple, Optional
import re

# Cấu hình trang
st.set_page_config(
    page_title="COVID-19 Health Assistant",
    page_icon="🏥",
    layout="wide"
)

# Load knowledge base và ontology
def load_knowledge_base() -> Tuple[Dict, Dict]:
    with open('data/covid.json', 'r', encoding='utf-8') as f:
        knowledge_base = json.load(f)
    with open('data/ontology/covid_ontology.json', 'r', encoding='utf-8') as f:
        ontology = json.load(f)
    return knowledge_base, ontology

# Khởi tạo knowledge base và ontology
knowledge_base, ontology = load_knowledge_base()

class OntologyMatcher:
    def __init__(self, ontology: Dict):
        self.ontology = ontology
        self.classes = ontology['ontology']['classes']
        self.relationships = ontology['ontology']['relationships']
        self.instances = ontology['ontology']['instances']
        
    def find_related_instances(self, instance_id: str) -> List[Dict]:
        """Tìm các instance liên quan dựa trên relationships"""
        related = []
        for instance_type, instances in self.instances.items():
            for instance in instances:
                if instance_id in instance.get('id', ''):
                    related.append(instance)
        return related
    
    def get_class_properties(self, class_name: str) -> Dict:
        """Lấy properties của một class"""
        return self.classes.get(class_name, {}).get('properties', {})
    
    def find_matching_instances(self, query: str) -> List[Dict]:
        """Tìm các instance phù hợp với query"""
        matches = []
        query = query.lower()
        
        for instance_type, instances in self.instances.items():
            for instance in instances:
                # Kiểm tra tên và các thuộc tính
                if any(query in str(value).lower() for value in instance.values()):
                    matches.append(instance)
        return matches

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

def find_related_categories(category: str, user_input: str) -> List[Tuple[str, str]]:
    """
    Tìm các danh mục liên quan dựa trên category và user_input
    """
    related = []
    category_mapping = {
        "trieu_chung": ["dieu_tri", "cap_cuu", "xet_nghiem"],
        "vac_xin": ["phong_ngua", "bien_the", "nhom_nguy_co"],
        "bien_the": ["vac_xin", "phong_ngua", "trieu_chung"],
        "dieu_tri": ["trieu_chung", "cap_cuu", "xet_nghiem"],
        "phong_ngua": ["vac_xin", "dinh_duong", "lam_viec_tai_nha"],
        "nhom_nguy_co": ["vac_xin", "dieu_tri", "cap_cuu"],
        "cap_cuu": ["trieu_chung", "dieu_tri", "xet_nghiem"],
        "xet_nghiem": ["trieu_chung", "dieu_tri", "cap_cuu"],
        "dinh_duong": ["phong_ngua", "dieu_tri", "trieu_chung"],
        "lam_viec_tai_nha": ["phong_ngua", "suc_khoe_tam_than"],
        "suc_khoe_tam_than": ["lam_viec_tai_nha", "dinh_duong"],
        "mang_thai": ["vac_xin", "nhom_nguy_co", "cap_cuu"],
        "tre_em": ["vac_xin", "trieu_chung", "cap_cuu"],
        "du_lich": ["phong_ngua", "xet_nghiem", "cap_cuu"],
        "myt_duong_tinh": ["dieu_tri", "trieu_chung", "suc_khoe_tam_than"]
    }
    
    # Lấy các danh mục liên quan
    related_cats = category_mapping.get(category, [])
    
    # Tìm thông tin từ các danh mục liên quan
    for cat in related_cats:
        if cat in knowledge_base['covid19_knowledge_base']['categories']:
            data = knowledge_base['covid19_knowledge_base']['categories'][cat]
            # Tìm câu trả lời phù hợp nhất trong danh mục liên quan
            best_match = None
            for qa in data['data']:
                if any(keyword in user_input.lower() for keyword in qa['keywords']):
                    best_match = (data['title'], qa['answer'])
                    break
            if best_match:
                related.append(best_match)
    
    return related

def find_best_match(user_input: str, ontology_matcher: OntologyMatcher) -> Tuple[Optional[str], str]:
    """
    Tìm câu trả lời phù hợp nhất cho câu hỏi của người dùng
    """
    # Chuẩn hóa input
    user_input = user_input.lower()
    
    best_match = None
    best_score = 0
    related_info = []
    all_matches = set()  # Sử dụng set để tránh trùng lặp
    
    # Tìm kiếm trong ontology
    ontology_matches = ontology_matcher.find_matching_instances(user_input)
    if ontology_matches:
        for match in ontology_matches:
            related = ontology_matcher.find_related_instances(match['id'])
            related_info.extend(related)
    
    # Tìm kiếm trong knowledge base
    for category, data in knowledge_base['covid19_knowledge_base']['categories'].items():
        # Kiểm tra intent với trọng số cao
        for intent in data['intent']:
            if intent in user_input:
                best_qa = random.choice(data['data'])
                score = len(intent) * 2  # Trọng số cao cho intent
                if score > best_score:
                    best_score = score
                    best_match = (data['title'], best_qa['answer'])
        
        # Kiểm tra các câu hỏi
        for qa in data['data']:
            # Kiểm tra câu hỏi trực tiếp
            question_words = qa['question'].lower().split()
            input_words = user_input.split()
            match_count = sum(1 for word in question_words if word in input_words)
            
            if match_count >= 2:  # Ít nhất 2 từ khớp
                score = match_count * 1.5
                if score > best_score:
                    best_score = score
                    best_match = (data['title'], qa['answer'])
            
            # Kiểm tra từ khóa
            for keyword in qa['keywords']:
                if keyword in user_input:
                    score = len(keyword)
                    if score > best_score:
                        best_score = score
                        best_match = (data['title'], qa['answer'])
                    # Thêm vào danh sách matches để hiển thị thông tin liên quan
                    all_matches.add((data['title'], qa['answer']))
    
    # Trích xuất triệu chứng
    symptoms = extract_symptoms(user_input)
    
    # Nếu tìm thấy kết quả tốt nhất
    if best_match:
        category, answer = best_match
        
        # Tìm thông tin liên quan
        related_categories = find_related_categories(category.lower().replace(" ", "_").replace("ứ", "u"), user_input)
        
        return category, format_response(category, answer, related_info[:3], symptoms, related_categories[:2])
    
    # Nếu không tìm thấy kết quả phù hợp
    return None, random.choice(knowledge_base['covid19_knowledge_base']['chatbot_responses']['fallback'])

def check_emergency(user_input: str) -> bool:
    """
    Kiểm tra xem câu hỏi có liên quan đến tình huống khẩn cấp không
    """
    emergency_keywords = knowledge_base['covid19_knowledge_base']['nlp_patterns']['emergency_keywords']
    return any(keyword in user_input.lower() for keyword in emergency_keywords)

def extract_symptoms(user_input: str) -> List[str]:
    """
    Trích xuất các triệu chứng từ câu hỏi của người dùng
    """
    symptom_keywords = knowledge_base['covid19_knowledge_base']['nlp_patterns']['symptom_keywords']
    return [symptom for symptom in symptom_keywords if symptom in user_input.lower()]

# Khởi tạo OntologyMatcher
ontology_matcher = OntologyMatcher(ontology)

# UI
st.title("🏥 COVID-19 Health Assistant")
st.write("Xin chào! Tôi là trợ lý ảo COVID-19. Tôi có thể giúp bạn tìm hiểu về COVID-19, triệu chứng, cách phòng ngừa và điều trị.")

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
        response = random.choice(knowledge_base['covid19_knowledge_base']['chatbot_responses']['emergency'])
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
st.sidebar.write("🚨 Cấp cứu:", knowledge_base['covid19_knowledge_base']['chatbot_responses']['contact_info']['emergency'])
st.sidebar.write("📞 Bộ Y tế:", knowledge_base['covid19_knowledge_base']['chatbot_responses']['contact_info']['health_ministry_hotline'])
st.sidebar.write("📞 COVID-19:", knowledge_base['covid19_knowledge_base']['chatbot_responses']['contact_info']['covid_hotline'])

# Hiển thị thông tin ontology
st.sidebar.title("Thông tin Ontology")
st.sidebar.write("Số lượng classes:", len(ontology['ontology']['classes']))
st.sidebar.write("Số lượng relationships:", len(ontology['ontology']['relationships']))
st.sidebar.write("Số lượng instances:", sum(len(instances) for instances in ontology['ontology']['instances'].values()))
