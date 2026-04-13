package dev.taha.cupid;

import android.os.Bundle;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    private TextView username;
    private TextView password;

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

        username = findViewById(R.id.editTextText);
        password = findViewById(R.id.editTextText2);

        username.setOnFocusChangeListener((v, hasFocus) -> {
            if (!hasFocus) {
                if (username.getText().toString().isEmpty()) {
                    username.setError("Username cannot be empty");
                }
            }
        });

        password.setOnFocusChangeListener((v, hasFocus) -> {
            if (!hasFocus) {
                if (password.getText().toString().isEmpty()) {
                    password.setError("Password cannot be empty");
                }
            }
        });

        findViewById(R.id.button14).setOnClickListener(v -> {
            if (username.getText().toString().isEmpty()) {
                username.setError("Username cannot be empty");
            }
            if (password.getText().toString().isEmpty()) {
                password.setError("Password cannot be empty");
            }

            if (!username.getText().toString().isEmpty() && !password.getText().toString().isEmpty()) {
                if (login(username.getText().toString(), password.getText().toString())) {
                    username.setError(null);
                    password.setError(null);
                    username.setText("");
                    password.setText("");
                } else {
                    username.setError("Invalid credentials");
                    password.setError("Invalid credentials");
                }
            }
        });
    }

    public Boolean login(String username, String password) {
        boolean isLogin = username == "admin" && password == "admin" ? false : true;
        return  isLogin;
    }
}