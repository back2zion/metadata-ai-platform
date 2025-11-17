import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

class QwenModel:
    def __init__(self, model_name="Qwen/Qwen3-8B"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """모델과 토크나이저 로드"""
        try:
            logger.info(f"Loading Qwen model: {self.model_name} on device: {self.device}")
            
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # 모델 로드 (메모리 최적화를 위해 4bit quantization 사용)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                load_in_4bit=True if torch.cuda.is_available() else False,
                bnb_4bit_compute_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            
            logger.info("Qwen model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Qwen model: {e}")
            return False
    
    def generate_response(self, query: str, user_type: str = "patient", max_length: int = 1000):
        """의료 질의에 대한 응답 생성"""
        if not self.model or not self.tokenizer:
            return "모델이 로드되지 않았습니다."
        
        # 사용자 타입별 시스템 프롬프트
        if user_type == "doctor":
            system_prompt = """당신은 서울아산병원의 전문 의료 AI입니다. 의료진의 질의에 대해 정확하고 전문적인 임상 정보를 제공합니다.
- 임상적 근거를 바탕으로 답변합니다
- 감별진단과 치료 옵션을 제시합니다
- 최신 의학 가이드라인을 참고합니다"""
        
        elif user_type == "researcher":
            system_prompt = """당신은 서울아산병원의 의료 연구 AI입니다. 연구자의 질의에 대해 과학적이고 데이터 기반의 정보를 제공합니다.
- 최신 연구 논문과 데이터를 참고합니다
- 통계적 분석과 연구 방법론을 제시합니다
- Evidence-based medicine 관점에서 답변합니다"""
        
        else:  # patient
            system_prompt = """당신은 서울아산병원의 친근한 의료 상담 AI입니다. 환자의 질문에 대해 이해하기 쉽고 안전한 정보를 제공합니다.
- 의학적 정보를 쉽게 설명합니다
- 필요시 병원 방문을 권고합니다
- 응급상황에서는 즉시 응급실 방문을 안내합니다
- 이 정보는 의학적 진단을 대체하지 않음을 명시합니다"""
        
        # 메시지 구성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        # 토큰화
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        try:
            # 생성
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **model_inputs,
                    max_new_tokens=max_length,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # 디코딩
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

    def generate_streaming_response(self, query: str, user_type: str = "patient"):
        """스트리밍 응답 생성"""
        try:
            response = self.generate_response(query, user_type)
            
            # 단어별로 스트리밍
            words = response.split()
            for word in words:
                yield word + " "
                
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield f"스트리밍 응답 생성 중 오류가 발생했습니다: {str(e)}"

# 전역 모델 인스턴스
qwen_model = QwenModel()