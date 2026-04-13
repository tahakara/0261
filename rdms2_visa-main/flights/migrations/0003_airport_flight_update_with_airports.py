# Generated manually for airport restructuring

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0002_rename_idx_passenger_address_passenger_idx_pass_addr_pass_and_more'),
    ]

    operations = [
        # Create Airport model
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('airport_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('airport_name', models.CharField(max_length=200, verbose_name='Airport Name')),
                ('iata_code', models.CharField(max_length=3, unique=True, verbose_name='IATA Code')),
                ('icao_code', models.CharField(max_length=4, unique=True, verbose_name='ICAO Code')),
                ('city', models.CharField(max_length=100, verbose_name='City')),
                ('country', models.CharField(max_length=100, verbose_name='Country')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Airport',
                'verbose_name_plural': 'Airports',
                'db_table': 'airports',
                'ordering': ['iata_code'],
            },
        ),
        # Add indexes to Airport
        migrations.AddIndex(
            model_name='airport',
            index=models.Index(fields=['iata_code'], name='idx_airport_iata'),
        ),
        migrations.AddIndex(
            model_name='airport',
            index=models.Index(fields=['icao_code'], name='idx_airport_icao'),
        ),
        migrations.AddIndex(
            model_name='airport',
            index=models.Index(fields=['city'], name='idx_airport_city'),
        ),
        # Remove old fields from Flight
        migrations.RemoveField(
            model_name='flight',
            name='departure_point',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='arrival_point',
        ),
        # Add new foreign key fields to Flight
        migrations.AddField(
            model_name='flight',
            name='departure_airport',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name='departures',
                to='flights.airport',
                verbose_name='Departure Airport',
            ),
        ),
        migrations.AddField(
            model_name='flight',
            name='arrival_airport',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name='arrivals',
                to='flights.airport',
                verbose_name='Arrival Airport',
            ),
        ),
        # Update Flight indexes
        migrations.AddIndex(
            model_name='flight',
            index=models.Index(fields=['departure_airport'], name='idx_flight_dept'),
        ),
        migrations.AddIndex(
            model_name='flight',
            index=models.Index(fields=['arrival_airport'], name='idx_flight_arr'),
        ),
    ]
