package dev.taha.heracles;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {

    Button button;
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

        // Retrieve the ListView
        ListView listView = findViewById(R.id.listView);

        // Create an ArrayAdapter using the string array and a default list item layout
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.ulkeler1, android.R.layout.simple_list_item_1);

        // Set the adapter to the ListView
        listView.setAdapter(adapter);

        // Set the item click listener
        listView.setOnItemClickListener(
                new AdapterView.OnItemClickListener() {
                    @Override
                    public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                        // Get the selected item text from ListView
                        String selectedItem = (String) parent.getItemAtPosition(position);
                        // Display the selected item text on TextView
                        Toast.makeText(getApplicationContext(), "ListView item clicked : " + selectedItem, Toast.LENGTH_SHORT).show();
                    }
                }
        );

        button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, MainActivity2.class);
                startActivity(intent);
            }
        });

    }

    public void goToMainActivity2(View view) {
        Intent intent = new Intent(this, MainActivity2.class);
        startActivity(intent);
    }
}