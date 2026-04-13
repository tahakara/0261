package dev.taha.fioana;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    private Button butonToplama, butonCikartma, butonCarpma, butonBolme;
    private EditText editTextSayi1, editTextSayi2;
    private TextView textViewSonuc, textViewUyari;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        butonToplama = findViewById(R.id.btnTopla);
        butonCikartma = findViewById(R.id.btnFark);
        butonCarpma = findViewById(R.id.btnCarp);
        butonBolme = findViewById(R.id.btnBolme);

        editTextSayi1 = findViewById(R.id.editTxtBirinciSayi);
        editTextSayi2 = findViewById(R.id.editTxtIkinciSayi);

        textViewSonuc = findViewById(R.id.txtViewSonuc);
        textViewUyari = findViewById(R.id.txtViewUyari);


        butonToplama.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        hesapla('+');
                    }
                }
        );

        butonCikartma.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        hesapla('-');
                    }
                }
        );
        butonCarpma.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        hesapla('*');
                    }
                }
        );
        butonBolme.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        hesapla('/');
                    }
                }
        );

    }

    public void hesapla(char islem) {
        String sayiStr1 = editTextSayi1.getText().toString();
        String sayiStr2 = editTextSayi2.getText().toString();

        if (sayiStr1.isEmpty() || sayiStr1.isBlank() || sayiStr2.isEmpty() || sayiStr2.isBlank()){
            textViewUyari.setVisibility(View.VISIBLE);
            textViewUyari.setText(" !!!! ");
        }

        else {
            textViewUyari.setVisibility(View.INVISIBLE);
            double sayi1 = Double.parseDouble(sayiStr1);
            double sayi2 = Double.parseDouble(sayiStr2);
            double sonuc = 0;
            boolean is_can_redirect=false;

            switch (islem) {
                case '+':
                    sonuc = sayi2 + sayi1;
                    is_can_redirect = true;
                    break;

                case '-':
                    sonuc = sayi1 - sayi2;
                    is_can_redirect = true;
                    break;

                case '*':
                    sonuc = sayi1 * sayi2;
                    is_can_redirect = true;
                    break;

                case '/':
                    if (sayi2 == 0){
                        textViewUyari.setVisibility(View.VISIBLE);
                        textViewUyari.setText("0 a bolemezsin");

                    }
                    else {
                        sonuc = sayi1/sayi2;
                        is_can_redirect = true;
                    }
                    break;

            }

            textViewSonuc.setVisibility(View.VISIBLE);
            textViewSonuc.setText(sayi1 + " "+ islem + " "+ sayi2 + "= " + sonuc);
            if (is_can_redirect == true) {
                ikinciyeGit(sonuc);

            }
        }
    }

    public void ikinciyeGit(double sonuc) {
        Intent niyet = new Intent(this, MainActivity2.class);
        niyet.putExtra("bim",sonuc);
        startActivity(niyet);
    }
}