package dev.taha.echo;

import android.os.Bundle;
import android.text.TextUtils;
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

    private EditText editTxtBirinciSayi, editTxtIkinciSayi;
    private TextView txtViewSonuc, txtViewUyari;
    private String biriciSayi, ikinciSayi;
    private String s1,s2,sonuc;
    private Calculator calculator;
    private Button btnTopla, btnFark, btnCarp, btnBolme;

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

        editTxtBirinciSayi = findViewById(R.id.editTxtBirinciSayi);
        editTxtIkinciSayi = findViewById(R.id.editTxtIkinciSayi);

        txtViewSonuc = findViewById(R.id.txtViewSonuc);
        txtViewUyari = findViewById(R.id.txtViewUyari);

        btnTopla = findViewById(R.id.btnTopla);

        btnTopla.setOnClickListener(
            new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    s1 = editTxtBirinciSayi.getText().toString();
                    s2 = editTxtIkinciSayi.getText().toString();
                    calculator = new Calculator();
                    if (!TextUtils.isEmpty(s1) && !TextUtils.isEmpty(s2)) {
                        sonuc = String.valueOf(calculator.topla(Integer.parseInt(s1), Integer.parseInt(s2)));
                        txtViewSonuc.setText("Sonuc " + sonuc);
                    }
                    else {
                        txtViewUyari.setText("Girilen Degerler Bos Olamaz");
                        txtViewUyari.setVisibility(View.VISIBLE);
                    }
                }
            }
        );

        btnFark = findViewById(R.id.btnFark);
        btnFark.setOnClickListener(
            new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    s1 = editTxtBirinciSayi.getText().toString();
                    s2 = editTxtIkinciSayi.getText().toString();
                    calculator = new Calculator();
                    if (!TextUtils.isEmpty(s1) && !TextUtils.isEmpty(s2)) {
                        sonuc = String.valueOf(calculator.cikar(Integer.parseInt(s1), Integer.parseInt(s2)));
                        txtViewSonuc.setText("Sonuc " + sonuc);
                    }
                    else {
                        txtViewUyari.setText("Girilen Degerler Bos Olamaz");
                        txtViewUyari.setVisibility(View.VISIBLE);
                    }
                }
            }
        );

        btnCarp = findViewById(R.id.btnCarp);

        btnCarp.setOnClickListener(
            new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    s1 = editTxtBirinciSayi.getText().toString();
                    s2 = editTxtIkinciSayi.getText().toString();
                    calculator = new Calculator();
                    if (!TextUtils.isEmpty(s1) && !TextUtils.isEmpty(s2)) {
                        sonuc = String.valueOf(calculator.carp(Integer.parseInt(s1), Integer.parseInt(s2)));
                        txtViewSonuc.setText("Sonuc " + sonuc);
                        txtViewUyari.setVisibility(View.VISIBLE);
                    }
                    else {
                        txtViewUyari.setText("Girilen Degerler Bos Olamaz");
                        txtViewUyari.setVisibility(View.VISIBLE);
                    }
                }
            }
        );
        btnBolme = findViewById(R.id.btnBolme);

        btnBolme.setOnClickListener(
            new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    s1 = editTxtBirinciSayi.getText().toString();
                    s2 = editTxtIkinciSayi.getText().toString();
                    calculator = new Calculator();
                    if (!TextUtils.isEmpty(s1) && !TextUtils.isEmpty(s2)) {
                        sonuc = String.valueOf(calculator.bol(Integer.parseInt(s1), Integer.parseInt(s2)));
                        txtViewSonuc.setText("Sonuc " + sonuc);
                    }
                    else {
                        txtViewUyari.setText("Girilen Degerler Bos Olamaz");
                        txtViewUyari.setVisibility(View.VISIBLE);
                    }
                }
            }
        );

    }
}

