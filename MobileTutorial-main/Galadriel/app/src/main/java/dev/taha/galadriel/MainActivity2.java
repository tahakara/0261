package dev.taha.galadriel;

import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity2 extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // EdgeToEdge.enable(this);
        // "setContentView(R.layout.activity_main2);
        // "ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
        // "    Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
        // "    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
        // "    return insets;
        // "});

        ImageView img = new ImageView(this);
        FrameLayout.LayoutParams imageParams = new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
        );

        img.setImageResource(R.drawable.Gravity);
        img.setLayoutParams(imageParams);

        TextView txt = new TextView(this);
        txt.setText("New York");
        txt.setTextColor(Color.parseColor("#ffffff"));
        txt.setPadding(10,10,10,10);

        FrameLayout.LayoutParams txtParams = new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.WRAP_CONTENT, FrameLayout.LayoutParams.WRAP_CONTENT
        );

        txtParams.gravity = Gravity.CENTER_HORIZONTAL | Gravity.BOTTOM;
        txt.setLayoutParams(txtParams);

        FrameLayout outsideLayout = new FrameLayout(this);
        outsideLayout.setLayoutParams(new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
        ));

        outsideLayout.addView(img);
        outsideLayout.addView(txt);
        setContentView(outsideLayout);

    }
}