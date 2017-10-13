// On YouTube, the tags for a video can be at most 500 characters long
// and each individual tag can be at most 30 characters long (I think).
// This little tool checks a comma-separated list to see if your tags
// are good to go. If there are any issues, it tells you!

$(document).ready(function(){
  $("#metadata").keyup(function(event){
    if(event.keyCode ==13){
      $("#submit").click()
    }
  });




});
function count(){
  let metadata = $("#metadata").val();
  let mdLength = metadata.length;
  console.log(mdLength);
  let mdDiff = mdLength-500;
  $("#mdLength").html(mdLength);
  if (mdDiff >= 0){
    $("#mdDiff").html("Need to reduce by <strong>"+mdDiff+"</strong> characters.");
  }
  else{
    $("#mdDiff").html("Lengthwise, this MD is <strong>good to go!</strong> But check below for tags that are too long.")
  }

  let output =''
  let tags = metadata.split(',');
  for (var i = 0; i<tags.length; i++){
    console.log(tags[i]);
    console.log(tags[i].length)
    if (tags[i].length >= 30){
      output = output + tags[i]+'<br>'
      console.log("hi!")
      $("#tags").html(output);
    }
    else {
      continue;
    }
  }
  if (output == ''){
    $("#tags").html("<strong>No bad tags!</strong>");
  }


  console.log(tags)
}
