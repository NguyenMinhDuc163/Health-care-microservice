from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from difflib import SequenceMatcher
from typing import List, Optional
import uvicorn

# Import các hàm cần thiết từ bot_chat.py
from bot_chat import (
    load_knowledge_base,
    load_ontology_data,
    find_best_answer,
    is_emergency,
    analyze_covid_symptoms,
    assess_covid_risk,
    generate_covid_recommendations
)

app = FastAPI(
    title="Healthcare Chatbot API",
    description="API cho hệ thống tư vấn sức khỏe AI",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    is_emergency: bool
    matched_disease: Optional[str] = None
    detected_symptoms: Optional[List[str]] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    recommendations: Optional[List[str]] = None

def format_response_for_client(response_text):
    """Format response cho client - loại bỏ markdown, giữ emoji và xuống dòng"""
    if not response_text:
        return ""
    
    # Loại bỏ markdown ** và *
    formatted = response_text.replace("**", "")
    formatted = formatted.replace("*", "")
    
    # Làm sạch format thừa
    formatted = formatted.replace('\n\n\n', '\n\n').strip()
    
    return formatted

# Load knowledge base và ontology khi khởi động API
kb = load_knowledge_base()
ontology_data = load_ontology_data()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Kiểm tra tin nhắn khẩn cấp
        if is_emergency(request.message):
            emergency_text = "⚠️ **CẢNH BÁO KHẨN CẤP!**\n\nVui lòng gọi ngay số cấp cứu 115 hoặc đến bệnh viện gần nhất nếu bạn đang gặp các triệu chứng nghiêm trọng như khó thở, đau ngực, môi xanh tím, hoặc mất ý thức."
            return ChatResponse(
                response=format_response_for_client(emergency_text),
                is_emergency=True
            )

        # Tìm câu trả lời từ knowledge base và ontology
        answer, matched_disease, detected_symptoms = find_best_answer(request.message, kb, ontology_data)

        if answer:
            # Loại bỏ tiêu đề cho social và symptom analysis
            if matched_disease in ["social", "symptom_analysis"]:
                response = answer['answer']
            else:
                response = f"**📋 {answer['question']}**\n\n{answer['answer']}"
            
            # Thêm phân tích triệu chứng nếu có
            risk_level = None
            confidence = None
            recommendations = None

            if detected_symptoms:
                if matched_disease == "covid19":
                    risk_level, confidence = assess_covid_risk(detected_symptoms)
                    recommendations = generate_covid_recommendations(detected_symptoms, risk_level)

            return ChatResponse(
                response=format_response_for_client(response),
                is_emergency=False,
                matched_disease=matched_disease,
                detected_symptoms=detected_symptoms,
                risk_level=risk_level,
                confidence=confidence,
                recommendations=recommendations
            )
        else:
            fallback_text = "Xin lỗi, tôi chưa có đủ thông tin để trả lời câu hỏi của bạn. Vui lòng thử hỏi lại theo cách khác hoặc liên hệ với bác sĩ để được tư vấn chi tiết hơn."
            return ChatResponse(
                response=format_response_for_client(fallback_text),
                is_emergency=False
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009) 