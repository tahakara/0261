package dev.taha.deathstar;

import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RelativeLayout;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        // setContentView(R.layout.activity_main);

        Button clickButton = new Button(this);
        RelativeLayout.LayoutParams buttonParams = new RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.WRAP_CONTENT, RelativeLayout.LayoutParams.WRAP_CONTENT);
        buttonParams.addRule(RelativeLayout.ALIGN_PARENT_RIGHT,RelativeLayout.TRUE);
        clickButton.setLayoutParams(buttonParams);
        clickButton.setText("Tıkla");
        clickButton.setId(261);

        EditText editText = new EditText(this);
        RelativeLayout.LayoutParams editTextParams = new RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.WRAP_CONTENT, RelativeLayout.LayoutParams.WRAP_CONTENT);
        editTextParams.addRule(RelativeLayout.ALIGN_PARENT_LEFT,RelativeLayout.TRUE);
        editTextParams.addRule(RelativeLayout.LEFT_OF,261);
        editText.setHint("merhaba dünya");
        editText.setLayoutParams(editTextParams);

        RelativeLayout outsideLayout = new RelativeLayout(this);
        RelativeLayout.LayoutParams outsideLayoutParams = new RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.MATCH_PARENT, RelativeLayout.LayoutParams.MATCH_PARENT);
        outsideLayout.addView(editText);
        outsideLayout.addView(clickButton);
        setContentView(outsideLayout);




    }
}