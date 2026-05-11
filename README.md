# 🛒 E-Commerce Sales Analysis and Recommendation System

This project is a data science-based e-commerce analysis dashboard and product recommendation system developed during a 72-hour Ideathon. It analyzes customers' past shopping data and offers personalized product recommendations using the **Cosine Similarity** algorithm.

## 🛠️ Technologies Used

- **Backend & Machine Learning:** Python, Scikit-learn, Pandas
- **Frontend & Interface:** Streamlit
- **Approach:** Collaborative Filtering

## 🚀 Installation and Execution

Follow the steps below to run the project on your local machine:

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

```

### 2. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt

```

### 3. Uygulamayı Başlatın

```bash
streamlit run dashboard/app.py

```

## 👥 Ekip ve Roller

* **Dilara:** Veri Mühendisi (Veri Temizleme & Hazırlama)
* **Eren:** Veri Analisti (Keşifsel Veri Analizi & Matris Oluşturma)
* **Adal:** Algoritma Lideri (Öneri Motoru Mimarisi & Backend)
* **Batuhan:** Arayüz Geliştirici (Dashboard & Kullanıcı Deneyimi)

## 📂 Proje Mimarisi (Klasör Yapısı)

Düzenli çalışmak için aşağıdaki klasör yapısına sadık kalıyoruz:

* **`data/`**: Veri setleri burada durur. Temizlenmiş ve analize hazır veriler.
* **`notebooks/`**: Deneme kodları ve analizler (Jupyter Notebook).
* **`src/`**: Projenin ana mantık kodları (Fonksiyonlar, recommender).
* **`dashboard/`**: Streamlit/Dash arayüz kodları.
* **`requirements.txt`**: Gerekli kütüphaneler.
