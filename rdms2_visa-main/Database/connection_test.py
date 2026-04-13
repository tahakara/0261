import psycopg2
from psycopg2 import OperationalError

def test_db_connection():
    # Bağlantı bilgilerini buraya girin
    connection_params = {
        "dbname": "aviation_sys",
        "user": "postgres",
        "password": "1234",
        "host": "100.64.207.39", # veya sunucu IP adresi
        "port": "5432"
    }

    connection = None
    try:
        print("PostgreSQL sunucusuna bağlanılıyor...")
        # Bağlantı kurmayı dene
        connection = psycopg2.connect(**connection_params)
        
        # Bir imleç (cursor) oluştur ve basit bir sorgu çalıştır
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("✅ Bağlantı Başarılı!")
        print(f"Sunucu Versiyonu: {db_version[0]}")
        
        cursor.close()

    except OperationalError as e:
        print(f"❌ Bağlantı Hatası: {e}")
    except Exception as e:
        print(f"⚠️ Beklenmedik bir hata oluştu: {e}")
    finally:
        # Bağlantı açıldıysa kapat
        if connection:
            connection.close()
            print("Bağlantı güvenli bir şekilde kapatıldı.")

if __name__ == "__main__":
    test_db_connection()