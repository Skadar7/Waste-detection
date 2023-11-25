const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
  });

async function getData(){
  let response = await fetch("/data");
  let str
  if (response.ok) { // если HTTP-статус в диапазоне 200-299
      // получаем тело ответа (см. про этот метод ниже)
      str = await response.text();
  } else {
      alert("Ошибка HTTP: " + response.status);
  }
  //alert(str)
  ///////////
  let url = "/xls"
    let options = {
        method: 'GET',
        headers: new Headers({
            'Content-Type': 'application/json',
        }),
        mode: 'cors',
        cache: 'default'
    };
    let strMimeType;
    let strFileName;

    //Perform a GET Request to server
    fetch(url, options)
    .then(function (response) {
        let contentType = response.headers.get("Content-Type"); //Get File name from content type
        strMimeType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
        strFileName = contentType.split(";")[1];
        return response.blob();

    }).then(function (myBlob) {
        let downloadLink = window.document.createElement('a');
        downloadLink.href = window.URL.createObjectURL(new Blob([myBlob], { type: strMimeType }));
        downloadLink.download = strFileName;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }).catch((e) => {
        console.log("e", e);
    });

}

async function workWithVideo(){

  if(document.getElementById("videoFile").files[0]=== undefined){
    alert("Вы не выбрали видео")
    return
  }
    let loadingGif = document.createElement("img")
    let div = document.getElementById("videoDiv")
    while (div.firstChild) {
      div.removeChild(div.firstChild);
    }
    loadingGif.src = "https://i.gifer.com/ZKZg.gif"
    loadingGif.id = "loadingGif"

    div.appendChild(loadingGif)


    let videoFile = document.getElementById("videoFile").files[0]
    
    let res_video = await toBase64(videoFile)
    let slv = res_video.split(",")
  
    var dataObj = {
      type : slv[0],
      b64 : slv[1],
      video_name : videoFile.name
    }
  
    var json = JSON.stringify(dataObj);
    
    div = document.getElementById("videoDiv")
    div.removeChild(loadingGif)
    requestVideo(json)
  }

  function requestVideo(json){
    var url = '/sendVideo';
      // Формируем запрос
      response = fetch(url, {
          // Метод, если не указывать, будет использоваться GET
          method: 'POST',
          // Заголовок запроса
          headers: {
          'Content-Type': 'application/json'
          },
          // Данные
          body: json
      })
      .then((resp) => resp.json())
      .then((data)=> finalVideo(data)
      );
  }
  
  function finalVideo(data)
  {
    //console.log(Object.keys(data));
    //console.log(Object.keys(data["video"]));
    //console.log(Object.keys(data["frames"]));
    //console.log(data["result"])
    

    document.getElementById("result").textContent = data["result"]
    document.getElementById("video_name").textContent = data["video_name"]
    var image = document.createElement("img")
    div = document.getElementById("videoDiv")
    div.appendChild(image)
    image.src = data["b64"]
    if (data["result"] == "No class"){
      image.src = "https://static.wikia.nocookie.net/memes9731/images/4/4e/Pepe-the-frog-internet-meme-sadness-know-your-meme-sad.jpg/revision/latest/thumbnail/width/360/height/360?cb=20200605055540&path-prefix=ru"
    }

    return
  }

  function startStream(){
    document.getElementById("content").src = "http://localhost:7000/video"

  }