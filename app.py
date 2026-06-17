import streamlit as st
import PyPDF2
import google.generativeai as genai
import json

GOOGLE_API_KEY = "AQ.Ab8RN6KV-zl0Kki28n0PViQKRXNu6cvrcXcaWN_2T_4G1wiUkg"
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="صانع الاختبارات الذكي", page_icon="📝", layout="centered")
st.title("📝 صانع الاختبارات الذكي")
st.write("ارفع ملف المراجعة (PDF) وحوّله إلى اختبار تفاعلي في ثوانٍ!")

# 2. واجهة رفع الملف
uploaded_file = st.file_uploader("اختر ملف المراجعة بصيغة PDF", type="pdf")

if uploaded_file is not None:
    # قراءة النص من الـ PDF
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    
    st.success("✅ تم قراءة الملف بنجاح!")
    
    # التأكد من وجود مفتاح الـ API
    if GOOGLE_API_KEY == "ضع_مفتاح_الـ_API_الخاص_بِك_هنا":
        st.warning("⚠️ يرجى وضع مفتاح الـ API الخاص بك في الكود لتفعيل الذكاء الاصطناعي وتوليد الأسئلة.")
    else:
        # 3. صياغة الأمر للذكاء الاصطناعي
        prompt = f"""
        اقرأ النص التالي واصنع منه اختباراً يتكون من 3 أسئلة خيارات متعددة (MCQ) باللغة العربية.
        يجب أن تكون الإجابة بصيغة JSON فقط، متبوعاً بهذا الهيكل تماماً دون أي كلام جانبي أو مقدمات:
        [
          {{
            "question": "السؤال هنا؟",
            "options": ["خيار 1", "خيار 2", "خيار 3", "خيار 4"],
            "answer": "الخيار الصحيح المطابق تماماً لواحد من الخيارات الأربعة"
          }}
        ]
        النص:
        {text}
        """
        
        # حفظ الأسئلة في الذاكرة المؤقتة للموقع حتى لا تتغير مع كل ضغطة زر
        if 'questions' not in st.session_state:
            with st.spinner("🧠 الذكاء الاصطناعي يقرأ الملف ويصنع الأسئلة..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    # تنظيف النص المستلم وتحويله لـ JSON
                    clean_text = response.text.strip().replace("```json", "").replace("```", "")
                    st.session_state.questions = json.loads(clean_text)
                except Exception as e:
                    st.error("حدث خطأ أثناء توليد الأسئلة، تأكد من صحة مفتاح الـ API وحاول مجدداً.")
                    st.stop()

        # 4. عرض الأسئلة للمستخدم
        if 'questions' in st.session_state:
            st.write("### ✍️ أجب عن الأسئلة التالية:")
            user_answers = {}
            
            for i, q in enumerate(st.session_state.questions):
                st.write(f"**س{i+1}: {q['question']}**")
                user_answers[i] = st.radio(f"اختر الإجابة لـ س{i+1}:", q['options'], key=f"q_{i}")
                st.write("---")
            
            # زر تصحيح الاختبار
            if st.button("تأكيد الإجابات ورؤية النتيجة 🎓"):
                score = 0
                total = len(st.session_state.questions)
                
                for i, q in enumerate(st.session_state.questions):
                    if user_answers[i] == q['answer']:
                        score += 1
                        st.success(f"س{i+1}: إجابة صحيحة! ✅")
                    else:
                        st.error(f"س{i+1}: إجابة خاطئة. ❌ الإجابة الصحيحة هي: {q['answer']}")
                
                st.balloons()
                st.metric(label="درجتك النهائية:", value=f"{score} من {total}") 