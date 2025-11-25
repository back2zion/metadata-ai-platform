# 케이뱅크(Kbank) 코퍼리트 컬러(Corporate Color) 가이드

## 브랜드 스토리

**슬로건**: 기분 좋은 금융생활

알고 계세요?
은행이 조금만 바뀌어도 우리 기분이 달라진다는 사실

이제 새로워진 케이뱅크와 함께
복잡했던 금융을 가깝고 편하게 만나고
매일을 기분 좋은 일상으로 만들어보세요.

케이뱅크와 만나는 모든 순간들이
즐거움으로 이어지도록
**기분 좋은 금융생활, Kbank**

---

## 메인 컬러 (Primary Colors)

### KBANK BLUE (Primary)
- **HEX**: #0114A7
- **RGB**: R(1), G(20), B(167)
- **Usage**: 주 브랜드 컬러, 버튼, 아이콘, 강조 요소, 헤더
- **의미**: 신뢰, 전문성, 금융의 안정성

### KBANK SECONDARY BLUE
- **HEX**: #4262FF
- **RGB**: R(66), G(98), B(255)
- **Usage**: 보조 브랜드 컬러, 호버 효과, 그라데이션
- **의미**: 혁신, 디지털 트랜스포메이션

## 서브 컬러 (Grayscale & Supporting Colors)

### KBANK LIGHT GRAY 1
- **HEX**: #E0E6F1
- **Usage**: 배경색, 구분선, 비활성 상태

### KBANK LIGHT GRAY 2
- **HEX**: #EDF1F7
- **Usage**: 카드 배경, 입력 필드 배경

### KBANK LIGHT GRAY 3
- **HEX**: #F7F9FD
- **Usage**: 페이지 배경, 섹션 구분

### WHITE
- **HEX**: #FFFFFF
- **Usage**: 메인 배경, 카드 배경, 텍스트

## 브랜드 적용 컬러 (Application Colors)

### Success Green
- **HEX**: #00B894 
- **Usage**: 성공 상태, 완료 메시지, 긍정적 피드백

### Warning Yellow
- **HEX**: #FDCB6E
- **Usage**: 경고, 주의 메시지, 대기 상태

### Error Red
- **HEX**: #E17055
- **Usage**: 오류 상태, 실패 메시지, 중요 경고

### Info Blue
- **HEX**: #6C5CE7 (Purple-Blue)
- **Usage**: 정보성 메시지, 툴팁, 가이드

## UI 적용 가이드

### 색상 계층 구조
1. **Primary**: KBANK BLUE (#0114A7) - 주요 액션, 로고, 브랜드 요소
2. **Secondary**: KBANK SECONDARY BLUE (#4262FF) - 보조 액션, 링크
3. **Success**: Success Green (#00B894) - 성공 상태, 완료
4. **Warning**: Warning Yellow (#FDCB6E) - 경고, 알림
5. **Error**: Error Red (#E17055) - 오류 상태
6. **Info**: Info Blue (#6C5CE7) - 정보성 메시지

### 배경 및 레이아웃
- **Main Background**: #F8F9FF (연한 블루 톤)
- **Card Background**: #FFFFFF
- **Header Background**: Linear Gradient (#0114A7 → #4262FF)
- **Sidebar Background**: #FFFFFF

### 그림자 및 투명도
- **Primary Shadow**: rgba(1, 20, 167, 0.08) - KBANK BLUE 기반
- **Card Shadow**: 0 4px 12px rgba(1, 20, 167, 0.08)
- **Button Shadow**: 0 4px 8px rgba(1, 20, 167, 0.24)

### 호버 효과
- **Menu Item Selected**: rgba(1, 20, 167, 0.12)
- **Menu Item Hover**: rgba(1, 20, 167, 0.08)

## 로고 및 브랜딩 가이드

### 브랜드명 사용법
- **국문**: 케이뱅크 (올바른)
- **영문**: Kbank (올바른)
- **대문자**: KBANK (허용)
- **소문자**: kbank (허용)
- **잘못된 예**: k뱅크, 케이 뱅크 (띄어쓰기)

### 로고 사용 규정
- 로고 주변 충분한 여백 확보
- 비례 변형 금지
- 지정된 컬러만 사용
- 배경색 고려하여 가시성 확보

### 서비스 아이콘
- 사각형/원형 아이콘 제공
- 다양한 배경색에 대응
- 최소 여백 규정 준수

## 브랜드 폰트

### 국문 폰트
- **Primary**: PretendardKEdition
- **Alternative**: Pretendard
- **Weights**: Light, Regular, Medium, Bold

### 영문 폰트
- **Primary**: Pretendard
- **Weights**: Light, Regular, Medium, Semibold

## 접근성 고려사항

### 대비율
- KBANK BLUE (#0114A7)과 흰색 텍스트: 높은 대비율 확보
- 연한 배경(#F8F9FF)에 검은 텍스트: 충분한 가독성
- Warning Yellow (#FDCB6E): 검은 텍스트와 조합

### 색맹 고려
- 색상만으로 정보 전달 금지
- 아이콘과 텍스트 병용
- 충분한 명도 대비 유지

## 구현 예시

```css
/* CSS Variables */
:root {
  --kbank-primary: #0114A7;
  --kbank-secondary: #4262FF;
  --kbank-success: #00B894;
  --kbank-warning: #FDCB6E;
  --kbank-error: #E17055;
  --kbank-info: #6C5CE7;
  --kbank-bg: #F8F9FF;
  --kbank-gray-1: #E0E6F1;
  --kbank-gray-2: #EDF1F7;
  --kbank-gray-3: #F7F9FD;
}

/* Primary Button */
.btn-primary {
  background-color: var(--kbank-primary);
  background-image: linear-gradient(135deg, var(--kbank-primary) 0%, var(--kbank-secondary) 100%);
  border: none;
  box-shadow: 0 4px 8px rgba(1, 20, 167, 0.24);
  border-radius: 12px;
}

/* Success State */
.success {
  color: var(--kbank-success);
}

/* Warning State */
.warning {
  color: var(--kbank-warning);
}

/* Header Gradient */
.header {
  background: linear-gradient(135deg, var(--kbank-primary) 0%, var(--kbank-secondary) 100%);
}
```

## Text2SQL 플랫폼 적용 상태

✅ **Ant Design Theme**: 모든 케이뱅크 브랜드 컬러 적용 완료  
✅ **Header Design**: 브랜드 그라데이션 및 로고 적용  
✅ **Component Colors**: 버튼, 카드, 아이콘 케이뱅크 색상 통일  
✅ **Interactive Elements**: 호버, 선택 상태 브랜드 색상 적용  
✅ **Typography**: 케이뱅크 전용 텍스트 색상 계층 구조 적용  
✅ **Background Theme**: 브랜드 연한 블루 배경(#F8F9FF) 적용  

---

**업데이트**: 2025-11-24  
**프로젝트**: 케이뱅크 Text2SQL 플랫폼  
**슬로건**: 기분 좋은 금융생활  
**적용 범위**: 전체 UI/UX 시스템  
**브랜드 자산**: https://brand.kbanknow.com/