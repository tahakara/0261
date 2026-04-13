package dev.taha.heracles;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity2 extends AppCompatActivity {
    Button button;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main2);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Retrieve the ListView
        ListView listView = findViewById(R.id.listView2);

        // Create an ArrayAdapter using the string array and a default list item layout
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.renkler, android.R.layout.simple_list_item_1);

        // Set the adapter to the ListView
        listView.setAdapter(adapter);

        // Set the item click listener
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                // Get the selected item text from ListView
                String selectedItem = (String) parent.getItemAtPosition(position);
                // Change the background color of the ListView based on the selected item
                switch (selectedItem) {
                    case "Red":
                        listView.setBackgroundColor(Color.RED);
                        break;
                    case "Green":
                        listView.setBackgroundColor(Color.GREEN);
                        break;
                    case "Blue":
                        listView.setBackgroundColor(Color.BLUE);
                        break;
                    case "Yellow":
                        listView.setBackgroundColor(Color.YELLOW);
                        break;
                    case "Black":
                        listView.setBackgroundColor(Color.BLACK);
                        break;
                }


            }
        });

        button = findViewById(R.id.button2);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity2.this, MainActivity.class);
                startActivity(intent);
            }
        });
    }

    public void goToMainActivity(View view) {
        Intent intent = new Intent(MainActivity2.this, MainActivity.class);
        startActivity(intent);
    }
}