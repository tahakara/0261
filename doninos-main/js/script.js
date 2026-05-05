var isDark = null;
function changeLoca(latitude, longitude) {
	var loc = `${latitude.toString()}, ${longitude.toString()}`;
	var locview = `${latitude.toString().substring(0,12)}, ${longitude.toString().substring(0,12)}`;
	setLocationToLocalStorage(latitude, longitude);
	document.querySelector(".dnns-delivery-loc > div > span").textContent = `${locview}`;
	document.querySelector(".dnns-delivery-loc > div > span").setAttribute("data-location",`${loc}`)
}

function showPosition(position) {
	// Print the latitude and longitude to the console
	console.log("Latitude: " + position.coords.latitude);
	console.log("Longitude: " + position.coords.longitude);
	
	changeLoca(position.coords.latitude, position.coords.longitude);
}

function showError(error) {
	// Handle different types of errors
	switch(error.code) {
		case error.PERMISSION_DENIED:
			alert("User denied the request for Geolocation.");
			break;
		case error.POSITION_UNAVAILABLE:
			alert("Location information is unavailable.");
			break;
		case error.TIMEOUT:
			alert("The request to get user location timed out.");
			break;
		case error.UNKNOWN_ERROR:
			alert("An unknown error occurred.");
			break;
	}
}

function isSet(userChoices) {
	if (userChoices != null) {

		var userChoices = JSON.parse(userChoices);
		if (userChoices.location != true) {
			changeLoca(userChoices.location.latitude, userChoices.location.longitude)
			changeDelivery()
		}
	}
	else {
		var item = {
			location : {
				latitude : null,
				longitude : null
			},
			delivery : 0 // 0 Delivery to home 1 In and Out
		}

		var userString = JSON.stringify(item);
		localStorage.setItem("user-choices", userString);
	}
}

function setLocationToLocalStorage(lat, lon) {
	var userChoices = localStorage.getItem("user-choices");
	if (userChoices != null) {
		userChoices = JSON.parse(userChoices);

		userChoices.location.latitude = lat;
		userChoices.location.longitude = lon;

		localStorage.setItem("user-choices",JSON.stringify(userChoices));
	}
}

function changeDelivery() {
	var userChoices = localStorage.getItem("user-choices");
	if (userChoices != null) {
		userChoices = JSON.parse(userChoices);

		switch (userChoices.delivery) {
			case 0:
				userChoices.delivery = 1;
				break;
				
			case 1:
				userChoices.delivery = 0;
				break;
		
			default:
				break;
		}

		var iconElement = document.querySelector(".dnns-delivery-opt > div > i");
		var textElement = document.querySelector(".dnns-delivery-opt > div > span");

		if (iconElement.classList.contains("fa-motorcycle")) {
		    iconElement.classList.remove("fa-motorcycle");
		    iconElement.classList.add("fa-utensils");
		    textElement.textContent = "In & Out";
		} else {
		    iconElement.classList.remove("fa-utensils");
		    iconElement.classList.add("fa-motorcycle");
		    textElement.textContent = "Home Delivery";
		}


		localStorage.setItem("user-choices",JSON.stringify(userChoices));
	}
}

function displayOpeningHours() {
    var openingHours = {
        0: "09:00 - 20:00",
        1: "09:00 - 20:00",
        2: "09:00 - 20:00",
        3: "09:00 - 20:00",
        5: "09:00 - 22:00",
        6: "10:00 - 22:00",
        7: "Closed"
    };

	var date = new Date()
	var day = date.getDay();
	
	var closed = `<i class="fa-solid fa-circle-xmark">${openingHours[day]}</i>`;
	var open = `<i class="fa-solid fa-check">${openingHours[day]}</i>`;

	document.querySelector("#isWorking").innerHTML = day >= 6 ? open : closed ;

}

function changeCartVisibilty() {
	var cartMenu = document.querySelector(".cartMenu");

	switch (cartMenu.style.display) {
		case (""):
			cartMenu.style.display = "block";
			break;

		case ("none" ):
			cartMenu.style.display = "block";
			break;
	
		case ("block"):
			cartMenu.style.display = "none";
			break;

		default:
			cartMenu.style.display = "none";
			break;
	}
}

function findItem(itemCode) {
	
	var products= [
		{
		  id: 1,
		  name: "Bol Malzemos",
		  image: "Bolmalzemos.jpg",
		  price:280,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Susam , Kekik"
		},
		{
		  id: 2,
		  name: "Mexicano",
		  image: "Mexicano.jpg",
		  price:300,
		  desc: "Mozarella Peyniri, Pizza Sos, Küp Köfte, Kırmızı Köz Biber, Acı Meksika Biberi, Soğan, Yöresel Lezzetler Baharatı"
		},
		{
		  id: 3,
		  name: "Cheddarlı Mexicano",
		  image: "Cheddarli_Mexicano.jpg",
		  price:310,
		  desc: "Mozarella Peyniri, Pizza Sos, Küp Köfte, Mantar, Mısır,Kırmızı Köz Biber, Yeşil Biber, Cheddar Peyniri, Soğan, Yöresel Lezzetler Baharatı"
		},
		{
		  id: 4,
		  name: "Extravaganzza",
		  image: "Extravaganzza.jpg",
		  price:290,
		  desc: "Jambon , Pepperoni , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Soğan , Mantar"
		},
		{
		  id: 5,
		  name: "Domino's Soslu Bol Malzemos",
		  image: "Doninos_Soslu_Bol_Malzemos.jpg",
		  price:290,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Dominos Sos , Susam , Kekik"
		},
		{
		  id: 6,
		  name: "Konyalım",
		  image: "Konyalim.jpg",
		  price:310,
		  desc: "Mozerella Peyniri , Pizza Sosu , Kavurma Eti , Soğan , Kırmızı Köz Biber , Yöresel Lezzetler Baharatı"
		},
		{
		  id: 7,
		  name: "Callypso",
		  image: "Callypso.jpg",
		  price:300,
		  desc: "Mısır , Mozarella Peyniri , Pizza Sos , Soğan , Domates , Ton Balığı"
		},
		{
		  id: 8,
		  name: "Karışık",
		  image: "Karisik.jpg",
		  price:280,
		  desc: "Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Yeşil Biber , Mantar"
		},
		{
		  id: 9,
		  name: "Pastırma & Sucuk",
		  image: "PastirmaAndSucuk.jpg",
		  price:300,
		  desc: "Mozerella Peyniri , Pizza Sosu , Pastirma , Sucuk , Domates , Yeşil Biber , Mantar"
		},
		{
		  id: 10,
		  name: "Bol Etli",
		  image: "Bol_Etli.jpg",
		  price:270,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis , Kırmızı Koz Biber , Mozarella Peyniri , Pizza Sos , Mantar , Küp Sucuk , Acı Meksika Biberi , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 11,
		  name: "Dopdolu Extra",
		  image: "Dopdolu_Extra.jpg",
		  price:290,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis ,Kırmızı Koz Biber , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Susam , Acı Meksika Biberi , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 12,
		  name: "Tavuklu",
		  image: "Tavuklu.jpg",
		  price:290,
		  desc: "Kırmızı Koz Biber , Mısır , Tavuk Parçaları , Mozarella Peyniri , Pizza Sos , Yeşil Biber , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 13,
		  name: "Üç Peynirli",
		  image: "Uc_Peynirli.jpg",
		  price:310,
		  desc: "Mozerella Peyniri , Cheddar Peyniri , Parmesan Peyniri , Pizza Sosu , Domates , Sarımsak Sos"
		},
		{
		  id: 14,
		  name: "Margarita",
		  image: "Margarita.jpg",
		  price:260,
		  desc: "Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 15,
		  name: "Domimix",
		  image: "Domimix.jpg",
		  price:280,
		  desc: "Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Mantar , Pastirma"
		},
		{
		  id: 16,
		  name: "Sosyal",
		  image: "Sosyal.jpg",
		  price:270,
		  desc: "Sucuk , Mısır , Mozarella Peyniri , Pizza Sos , Domates , Mantar , Kekik"
		},
		{
		  id: 17,
		  name: "Vegi",
		  image: "Vegi.jpg",
		  price:270,
		  desc: "Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Susam , Kekik"
		},
		{
		  id: 18,
		  name: "Mangal Sucuklu",
		  image: "Mangal_Sucuklu.jpg",
		  price:300,
		  desc: "Mozarella Peyniri , Pizza Sos , Yeşil Biber , Mantar , Mangal Sucuk"
		},
		{
		  id: 19,
		  name: "Mantarsever",
		  image: "Mantarsever.jpg",
		  price:260,
		  desc: "Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Mantar , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 20,
		  name: "Bol Sucuksever",
		  image: "Bol_Sucuksever.jpg",
		  price:260,
		  desc: "Sucuk , Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 21,
		  name: "Peperonni",
		  image: "Peperonni.jpg",
		  price:270,
		  desc: "Peperonni , Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 22,
		  name: "Cheddarlı Dev Sosisli",
		  image: "Cheddarli_Dev_Sosisli.jpg",
		  price:300,
		  desc: "Dev Sosis , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Cheddar Peyniri"
		},
		{
		  id: 23,
		  name: "Sarımsak Soslu Bol Sucuksever",
		  image: "Sarimsak_Soslu_Bol_Sucuksever.jpg",
		  price:270,
		  desc: "Sucuk , Mozarella Peyniri , Pizza Sos , Sarımsak Sos"
		},
		{
		  id: 24,
		  name: "Kantin",
		  image: "Kantin.jpg",
		  price:270,
		  desc: "Sosis , Mısır , Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 25,
		  name: "Favori İkili",
		  image: "Favori_Ikili.jpg",
		  price:270,
		  desc: "Jambon , Mozarella Peyniri , Pizza Sos , Mantar"
		},
		{
		  id: 26,
		  name: "Italiano",
		  image: "Italiano.jpg",
		  price:280,
		  desc: "Kırmızı Koz Biber , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Mantar , Küp Sucuk , Kekik"
		},
		{
		  id: 27,
		  name: "Süperos",
		  image: "Superos.jpg",
		  price:270,
		  desc: "Jambon , Sucuk , Sosis , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Domates , Kekik"
		},
		{
		  id: 28,
		  name: "Dev Malzemos",
		  image: "Dev_Malzemos.jpg",
		  price:290,
		  desc: "Sucuk , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Dev Sosis"
		},
		{
		  id: 29,
		  name: "Süperix",
		  image: "Superix.jpg",
		  price:260,
		  desc: "Sucuk , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin"
		},
		{
		  id: 30,
		  name: "Ocakbaşı",
		  image: "Ocakbasi.jpg",
		  price:310,
		  desc: "Sucuk , Kırmızı Koz Biber , Mozarella Peyniri , Pizza Sos , Yeşil Biber , Mantar , Pastirma , Kavurma Eti"
		},
		{
		  id: 31,
		  name: "Ballı Hardallı Tavuklu",
		  image: "Balli_Hardalli_Tavuklu.jpg",
		  price: 290,
		  desc: "Mozarella Peyniri , Pizza Sos , Tavuk Parçaları , Soğan , Mantar , Ballı Hardal Sos"
		}
	];

	products.forEach(product => {
		if(product.id == itemCode) {
			return product; // Assign the matched product, not the whole array
		}
	});
}

function addToCart(itemCode) {

	var prod = null;
	
	var products= [
		{
		  id: 1,
		  name: "Bol Malzemos",
		  image: "Bolmalzemos.jpg",
		  price:280,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Susam , Kekik"
		},
		{
		  id: 2,
		  name: "Mexicano",
		  image: "Mexicano.jpg",
		  price:300,
		  desc: "Mozarella Peyniri, Pizza Sos, Küp Köfte, Kırmızı Köz Biber, Acı Meksika Biberi, Soğan, Yöresel Lezzetler Baharatı"
		},
		{
		  id: 3,
		  name: "Cheddarlı Mexicano",
		  image: "Cheddarli_Mexicano.jpg",
		  price:310,
		  desc: "Mozarella Peyniri, Pizza Sos, Küp Köfte, Mantar, Mısır,Kırmızı Köz Biber, Yeşil Biber, Cheddar Peyniri, Soğan, Yöresel Lezzetler Baharatı"
		},
		{
		  id: 4,
		  name: "Extravaganzza",
		  image: "Extravaganzza.jpg",
		  price:290,
		  desc: "Jambon , Pepperoni , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Soğan , Mantar"
		},
		{
		  id: 5,
		  name: "Domino's Soslu Bol Malzemos",
		  image: "Doninos_Soslu_Bol_Malzemos.jpg",
		  price:290,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Dominos Sos , Susam , Kekik"
		},
		{
		  id: 6,
		  name: "Konyalım",
		  image: "Konyalim.jpg",
		  price:310,
		  desc: "Mozerella Peyniri , Pizza Sosu , Kavurma Eti , Soğan , Kırmızı Köz Biber , Yöresel Lezzetler Baharatı"
		},
		{
		  id: 7,
		  name: "Callypso",
		  image: "Callypso.jpg",
		  price:300,
		  desc: "Mısır , Mozarella Peyniri , Pizza Sos , Soğan , Domates , Ton Balığı"
		},
		{
		  id: 8,
		  name: "Karışık",
		  image: "Karisik.jpg",
		  price:280,
		  desc: "Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Yeşil Biber , Mantar"
		},
		{
		  id: 9,
		  name: "Pastırma & Sucuk",
		  image: "PastirmaAndSucuk.jpg",
		  price:300,
		  desc: "Mozerella Peyniri , Pizza Sosu , Pastirma , Sucuk , Domates , Yeşil Biber , Mantar"
		},
		{
		  id: 10,
		  name: "Bol Etli",
		  image: "Bol_Etli.jpg",
		  price:270,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis , Kırmızı Koz Biber , Mozarella Peyniri , Pizza Sos , Mantar , Küp Sucuk , Acı Meksika Biberi , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 11,
		  name: "Dopdolu Extra",
		  image: "Dopdolu_Extra.jpg",
		  price:290,
		  desc: "Jambon , Pepperoni , Sucuk , Sosis ,Kırmızı Koz Biber , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Susam , Acı Meksika Biberi , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 12,
		  name: "Tavuklu",
		  image: "Tavuklu.jpg",
		  price:290,
		  desc: "Kırmızı Koz Biber , Mısır , Tavuk Parçaları , Mozarella Peyniri , Pizza Sos , Yeşil Biber , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 13,
		  name: "Üç Peynirli",
		  image: "Uc_Peynirli.jpg",
		  price:310,
		  desc: "Mozerella Peyniri , Cheddar Peyniri , Parmesan Peyniri , Pizza Sosu , Domates , Sarımsak Sos"
		},
		{
		  id: 14,
		  name: "Margarita",
		  image: "Margarita.jpg",
		  price:260,
		  desc: "Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 15,
		  name: "Domimix",
		  image: "Domimix.jpg",
		  price:280,
		  desc: "Sucuk , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Mantar , Pastirma"
		},
		{
		  id: 16,
		  name: "Sosyal",
		  image: "Sosyal.jpg",
		  price:270,
		  desc: "Sucuk , Mısır , Mozarella Peyniri , Pizza Sos , Domates , Mantar , Kekik"
		},
		{
		  id: 17,
		  name: "Vegi",
		  image: "Vegi.jpg",
		  price:270,
		  desc: "Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Yeşil Biber , Domates , Mantar , Susam , Kekik"
		},
		{
		  id: 18,
		  name: "Mangal Sucuklu",
		  image: "Mangal_Sucuklu.jpg",
		  price:300,
		  desc: "Mozarella Peyniri , Pizza Sos , Yeşil Biber , Mantar , Mangal Sucuk"
		},
		{
		  id: 19,
		  name: "Mantarsever",
		  image: "Mantarsever.jpg",
		  price:260,
		  desc: "Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Mantar , Yöresel Lezzetleri Baharat"
		},
		{
		  id: 20,
		  name: "Bol Sucuksever",
		  image: "Bol_Sucuksever.jpg",
		  price:260,
		  desc: "Sucuk , Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 21,
		  name: "Peperonni",
		  image: "Peperonni.jpg",
		  price:270,
		  desc: "Peperonni , Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 22,
		  name: "Cheddarlı Dev Sosisli",
		  image: "Cheddarli_Dev_Sosisli.jpg",
		  price:300,
		  desc: "Dev Sosis , Sosis , Mısır , Mozarella Peyniri , Pizza Sos , Cheddar Peyniri"
		},
		{
		  id: 23,
		  name: "Sarımsak Soslu Bol Sucuksever",
		  image: "Sarimsak_Soslu_Bol_Sucuksever.jpg",
		  price:270,
		  desc: "Sucuk , Mozarella Peyniri , Pizza Sos , Sarımsak Sos"
		},
		{
		  id: 24,
		  name: "Kantin",
		  image: "Kantin.jpg",
		  price:270,
		  desc: "Sosis , Mısır , Mozarella Peyniri , Pizza Sos"
		},
		{
		  id: 25,
		  name: "Favori İkili",
		  image: "Favori_Ikili.jpg",
		  price:270,
		  desc: "Jambon , Mozarella Peyniri , Pizza Sos , Mantar"
		},
		{
		  id: 26,
		  name: "Italiano",
		  image: "Italiano.jpg",
		  price:280,
		  desc: "Kırmızı Koz Biber , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Mantar , Küp Sucuk , Kekik"
		},
		{
		  id: 27,
		  name: "Süperos",
		  image: "Superos.jpg",
		  price:270,
		  desc: "Jambon , Sucuk , Sosis , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Domates , Kekik"
		},
		{
		  id: 28,
		  name: "Dev Malzemos",
		  image: "Dev_Malzemos.jpg",
		  price:290,
		  desc: "Sucuk , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin , Dev Sosis"
		},
		{
		  id: 29,
		  name: "Süperix",
		  image: "Superix.jpg",
		  price:260,
		  desc: "Sucuk , Mısır , Mozarella Peyniri , Pizza Sos , Siyah Zeytin"
		},
		{
		  id: 30,
		  name: "Ocakbaşı",
		  image: "Ocakbasi.jpg",
		  price:310,
		  desc: "Sucuk , Kırmızı Koz Biber , Mozarella Peyniri , Pizza Sos , Yeşil Biber , Mantar , Pastirma , Kavurma Eti"
		},
		{
		  id: 31,
		  name: "Ballı Hardallı Tavuklu",
		  image: "Balli_Hardalli_Tavuklu.jpg",
		  price: 290,
		  desc: "Mozarella Peyniri , Pizza Sos , Tavuk Parçaları , Soğan , Mantar , Ballı Hardal Sos"
		}
	];

	products.forEach(product => {
		if(product.id == itemCode) {
			prod = product; // Assign the matched product, not the whole array
		}
	});

	var cartItem = `
		<div class="col-md-12 cart-item" data-item-name="{itemName}" data-item-price="{itemPrice}" >
			<div class="row" >

				<div class="col-md-3">
					<img src="{itemImage}" class="cart-item-image" alt="" srcset="" >
				</div>
				<div class="col-md-5 cart-item-name-parent">
					<div class="cart-item-name">
						{itemName}
					</div>
				</div>
				<div class="col-md-3 cart-item-price-parent">
					<div class="cart-item-price" >
						{itemPrice} TL
					</div>
				</div>
				<div class="col-md-1 cart-item-delete-parent" onclick="removeFromCart(event)">
					<i class="fa-regular fa-trash-can cart-item-delete"></i>
				</div>
			</div>
		</div>
	`;

	var cartTotal = `
		<div class="col-md-12 cart-item cart-total" data-item-name="" data-item-price="" >
			<div class="row" >
				<div class="col-md-6 cart-total-item-parent">
					<div class="cart-total-item">
						Total ({itemCount} item) : 
					</div>
				</div>
				<div class="col-md-4 cart-total-price-parent">
					<div class="cart-total-price" >
						{itemTotalPrice} TL
					</div>
				</div>
				<div class="col-md-1 cart-total-pay-parent">
					<i class="fa-regular fa-credit-card cart-total-pay" ></i>
				</div>
			</div>
		</div>
	`;

	var cartList = document.querySelector(".cart-list");
	cartList.innerHTML = "";

	var cart = localStorage.getItem("user-cart");

	if (cart != null) {
		cart = JSON.parse(cart);
		
		cart.cartItems.push ({
			itemName: prod.name,
			itemImage: "images/"+prod.image,
			itemPrice: prod.price
		});

		cart.cartTotal = cart.cartItems.length;
		var temp = 0;
		cart.cartItems.forEach(item => {
			temp += item.itemPrice;
			cartList.innerHTML += cartItem.replace('{itemImage}', item.itemImage).replace('{itemName}', item.itemName).replace('{itemPrice}', item.itemPrice).replace('{itemName}', item.itemName).replace('{itemPrice}', item.itemPrice);

		});

		cart.cartTotalPrice = temp;
		cartList.innerHTML += cartTotal.replace('{itemCount}', cart.cartTotal).replace('{itemTotalPrice}', cart.cartTotalPrice);

		localStorage.setItem("user-cart", JSON.stringify(cart))

	} else {
		cart = {
			cartItems:[],
			cartTotalItem: 0,
			cartTotalPrice: 0
		}

		cart.cartItems.push ({
			itemName: prod.name,
			itemImage: "images/"+prod.image,
			itemPrice: prod.price
		});

		cart.cartTotal = cart.cartItems.length;
		cart.cartItems.forEach(item => {
			cart.cartTotalPrice += item.itemPrice;
			cartList.innerHTML += cartItem.replace('{itemImage}', item.itemImage).replace('{itemName}', item.itemName).replace('{itemPrice}', item.itemPrice).replace('{itemName}', item.itemName).replace('{itemPrice}', item.itemPrice);

		});

		cartList.innerHTML += cartTotal.replace('{itemCount}', cart.cartTotalItem).replace('{itemTotalPrice}', cart.cartTotalPrice);

		localStorage.setItem("user-cart", JSON.stringify(cart))
	}
}

function updateCart() {
	var cartItem = `
		<div class="col-md-12 cart-item" data-item-name="{itemName}" data-item-price="{itemPrice}" >
			<div class="row" >

				<div class="col-md-3">
					<img src="{itemImage}" class="cart-item-image" alt="" srcset="" >
				</div>
				<div class="col-md-5 cart-item-name-parent">
					<div class="cart-item-name">
						{itemName}
					</div>
				</div>
				<div class="col-md-3 cart-item-price-parent">
					<div class="cart-item-price" >
						{itemPrice} TL
					</div>
				</div>
				<div class="col-md-1 cart-item-delete-parent" onclick="removeFromCart(event)">
					<i class="fa-regular fa-trash-can cart-item-delete"></i>
				</div>
			</div>
		</div>
	`;

	var cartTotal = `
		<div class="col-md-12 cart-item cart-total" data-item-name="" data-item-price="" >
			<div class="row" >
				<div class="col-md-6 cart-total-item-parent">
					<div class="cart-total-item">
						Total ({itemCount} item) : 
					</div>
				</div>
				<div class="col-md-4 cart-total-price-parent">
					<div class="cart-total-price" >
						{itemTotalPrice} TL
					</div>
				</div>
				<div class="col-md-1 cart-total-pay-parent">
					<i class="fa-regular fa-credit-card cart-total-pay" ></i>
				</div>
			</div>
		</div>
	`;

	var cartList = document.querySelector(".cart-list");
	cartList.innerHTML = "";

	var cart = localStorage.getItem("user-cart");

	if (cart != null) {
		cart = JSON.parse(cart);
		console.log(cart)
		var temp=0;
		var temp1=0;
		cart.cartItems.forEach(item => {
			temp += item.itemPrice;
			temp1 += 1;
			cartList.innerHTML += cartItem.replace('{itemImage}', item.itemImage).replace('{itemName}', item.itemName).replace('{itemPrice}', item.itemPrice).replace('{itemName}', item.itemName).replace('{itemPrice}', item.itemPrice);
		});

		cart.cartTotalPrice = temp;
		cart.cartTotalItem = temp1;
		cartList.innerHTML += cartTotal.replace('{itemCount}', cart.cartTotalItem).replace('{itemTotalPrice}', cart.cartTotalPrice);

		localStorage.setItem("user-cart", JSON.stringify(cart))

	} else {
		cart = {
			cartItems:[],
			cartTotalItem: 0,
			cartTotalPrice: 0
		}

		localStorage.setItem("user-cart", JSON.stringify(cart))
	}
	updateCartCounter()
}

function clearCart() {
	localStorage.removeItem("user-cart");
	updateCart();
}

function removeFromCart(event) {
    var targetElement = event.target;

    var parent = targetElement.closest('.cart-item');
    var itemName = parent.getAttribute("data-item-name");
    var itemPrice = parent.getAttribute("data-item-price");

    removeItemFromCart(itemName, itemPrice);
}

function removeItemFromCart(itemName, itemPrice) {
	var userCart = localStorage.getItem("user-cart");
	if (userCart != null) {
		userCart = JSON.parse(localStorage.getItem("user-cart"));
		console.log(userCart);
		console.log("adasdasdsdas1")
		for (let index = 0; index < userCart.cartItems.length; index++) {
			var element = userCart.cartItems[index];
			console.log(element)
			if (element.itemName == itemName && element.itemPrice == itemPrice) {
				userCart.cartTotalItem -=1;
				userCart.cartTotalPrice -= itemPrice;
				delete userCart.cartItems[index];
				var newCart = {};
				
				newCart.cartItems = [];
				newCart.cartTotalItem = userCart.cartTotalItem;
				newCart.cartTotalPrice = userCart.cartTotalPrice;
				
				for (let i = 0; i < userCart.cartItems.length; i++) {
					var element = userCart.cartItems[i];

					if (element != null) {
						newCart.cartItems.push(element);
					}

					
				}
				
				localStorage.setItem("user-cart", JSON.stringify(newCart));
				console.log("adasdasdsdas3")
				break;
			}
			
		}

		updateCart();
	} else {
		clearCart();
	}
}

function updateCartCounter() {
    var userCart = localStorage.getItem("user-cart");
    if (userCart !== null) {
        userCart = JSON.parse(userCart);
        console.log(userCart);
        var count = userCart.cartItems.length;

        document.querySelector(".cart-icon-span").innerHTML = count > 0 ?`<i class="fa-solid fa-cart-shopping" alt="cart"></i> ` + count : `<i class="fa-solid fa-cart-shopping" alt="cart"></i>`;
    } else {
        document.querySelector(".cart-icon-span").innerHTML = `<i class="fa-solid fa-cart-shopping" alt="cart"></i>`;
    }
}

function applyDarkMode() {
	if ($('.dnns-dark-mode input[type="checkbox"]').is(':checked')) {
		console.log("Dark mode enabled");
		$(".dnns-body").css("background-color", "#000000");
		$("body").css("background-color", "#f0f0f7");
		$(".dnns-product").css("background-color", "#f0f0f7");
		isDark = true;
	} else {
		console.log("Dark mode disabled");
		$(".dnns-body").css("background-color", "#f0f0f7");
		$("body").css("background-color", "#f0f0f7");
		$(".dnns-product").css("background-color", "#ffffff");
		isDark = false;
	}
}

$(document).ready(function() {
	var scrollToTopBtn = $("#scrollToTopBtn");

	var userChoices = localStorage.getItem("user-choices");
	
	displayOpeningHours()
	isSet(userChoices)
	updateCart()

	$("body").css({
		"user-select":"none"
	})

	// random hover color
	$('.dnns-header-naw-row > div > a').hover(function() {
		$(this).css({
			"color" : Math.random()>0.5 ? "#006490" : "#E31836",
			"transition" : "transform 0.3s ease"
		});
	}, function() {
		$(this).css({
			"color" : "#FFFFFF",
			"transition" : "transform 0.3s ease"
		});
	});

	$('.dnns-header-cart > a').hover(function() {
		$(".dnns-header-cart > a > span > i").css({
			"color" : "#cacacd",
			"transition" : "transform 0.3s ease"
		});
	}, function() {
		$(".dnns-header-cart > a > span > i").css({
			"color" : "#FFFFFF",
			"transition" : "transform 0.3s ease"
		});
	});

	$('.dnns-delivery-opt').on("click" ,function() {
		changeDelivery()
	});

	$(".dnns-delivery-loc").on("click", function(){
		if (navigator.geolocation) {
			console.log("asdsadsd")
			navigator.geolocation.getCurrentPosition(showPosition, showError);
		} else {
			console.log("Geolocation is not supported by this browser.");
		}
	});

	$(window).scroll(function() {
		if ($(this).scrollTop() > 20) {
			scrollToTopBtn.show();
		} else {
			scrollToTopBtn.hide();
		}
	});

	scrollToTopBtn.click(function() {
		$("html, body").animate({ scrollTop: 0 }, "smooth");
	});

	// $(".dnns-header-cart").on("click", function() {
	// 	console.log("a")
	// 	changeCartVisibilty()
	// });
	
	$(".dnns-header-cart > a").on("click", function() {
		console.log("b")
		changeCartVisibilty()
	});

	$(".dnns-product-detail-buy").on("click", function() {
		var itemCode = $(this).find("a").attr("data-dnns-prduct-id")
		addToCart(parseInt(itemCode))
	});

	$(document).on("click", function(){
		updateCartCounter()
	});

	$('.dnns-dark-mode input[type="checkbox"]').on('change', function() {
		applyDarkMode();
	});

	$('.dnns-product').hover(function() {
		if (!isDark) {
			$(this).css({
				"background-color" : "#ede8e89c",
				"transition" : "transform 0.3s ease"
			});
		}
			
	}, function() {
		if (!isDark) {
			$(this).css({
				"background-color" : "#FFFFFF",
				"transition" : "transform 0.3s ease"
			});
		}
	});

	$('.dnns-product-detail-buy').hover(function() {
		$(this).css({
			"color" : "#505061",
			"background-color" : "#3E4959",
			"transition" : "transform 0.3s ease"
		});

		$(this).find("a").find("span").css({
			"color" : "#FFFFFF",
			"transition" : "transform 0.3s ease"
		});
	}, function() {
		$(this).css({
			"color" : "#3e4959",
			"background-color" : "#ffffff",
			"transition" : "transform 0.3s ease"
		});
		$(this).find("a").find("span").css({
			"color" : "#3E4959",
			"transition" : "transform 0.3s ease"
		});
	});

	$('.dnns-product').hover(function() {
		$(this).find(".dnns-product-img").css({
			"transform" : "scale(1.05)",
			"box-shadow" : "0 0 10px 0 rgba(0, 0, 0, 0.5)",
            "transition" : "transform 0.3s ease"
		});
	}, function() {
		$(this).find(".dnns-product-img").css({
			"transform" : "scale(1)",
			"box-shadow" : "none",
            "transition": "transform 0.3s ease"
		});
	});
});


