package dev.taha.timerproject;

import android.os.Bundle;
import android.os.CountDownTimer;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.constraintlayout.widget.ConstraintLayout.LayoutParams;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    // Nexus 4
    // Android API 29 (Q)

    Button startButton, pauseButton, resetButton;
    TextView counterDisplayText;

    private CountDownTimer countDownTimer;
    private boolean isTimerRunning = false;
    private long timeLeftInMillis = 60000;

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

        startButton = findViewById(R.id.startButton);
        pauseButton = findViewById(R.id.pauseButton);
        resetButton = findViewById(R.id.resetButton);
        counterDisplayText = findViewById(R.id.counterDisplayText);

        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!isTimerRunning) {
                    startTimer(timeLeftInMillis);
                }
            }
        });

        pauseButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isTimerRunning) {
                    pauseTimer();
                }
            }
        });

        resetButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resetTimer();
            }
        });

    }

    private void startTimer(long timeInMillis) {
        startButton.setEnabled(false);
        pauseButton.setEnabled(true);
        resetButton.setEnabled(false);
        countDownTimer = new CountDownTimer(timeInMillis, 1000) {
            @Override
            public void onTick(long millisUntilFinished) {
                timeLeftInMillis = millisUntilFinished;
                long secondsRemaining = millisUntilFinished / 1000;
                counterDisplayText.setText("Saniye Kaldı: " + secondsRemaining);
            }

            @Override
            public void onFinish() {
                startButton.setEnabled(true);
                pauseButton.setEnabled(false);
                resetButton.setEnabled(false);
                isTimerRunning = false;
                counterDisplayText.setText(R.string.Done);
                softResetTimer();
            }
        }.start();

        isTimerRunning = true;
    }

    private void pauseTimer() {
        startButton.setEnabled(true);
        pauseButton.setEnabled(false);
        resetButton.setEnabled(true);

        countDownTimer.cancel();
        isTimerRunning = false;
    }

    private void resetTimer() {
        startButton.setEnabled(true);
        pauseButton.setEnabled(false);
        resetButton.setEnabled(false);
        if (countDownTimer != null) {
            countDownTimer.cancel();
        }
        timeLeftInMillis = 60000; // Reset to 60 seconds
        counterDisplayText.setText("Saniye Kaldi" + timeLeftInMillis / 1000);
        isTimerRunning = false;
    }

    private  void softResetTimer() {
        if (countDownTimer != null) {
            countDownTimer.cancel();
        }
        timeLeftInMillis = 60000; // Reset to 60 seconds
        isTimerRunning = false;
    }

}
