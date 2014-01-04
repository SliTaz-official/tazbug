// SliTaz Bugs Javascript functions.
//

// Check form to avoid empty values and bad email.
function checkNewBug() {
	if(document.forms["addbug"]["title"].value == "")
    {
        alert("Please enter a title for the new bug");
        document.forms["addbug"]["title"].focus();
        return false;
    }
    if(document.forms["addbug"]["desc"].value == "")
    {
        alert("Please fill in the bug description");
        document.forms["addbug"]["desc"].focus();
        return false;
    }
}

// Check form to avoid empty values and bad email.
function checkSignup() {
	if(document.forms["signup"]["name"].value == "")
    {
        alert("Please enter your real name");
        document.forms["signup"]["name"].focus();
        return false;
    }
    if(document.forms["signup"]["user"].value == "")
    {
        alert("Please fill in your user name");
        document.forms["signup"]["user"].focus();
        return false;
    }
	var x=document.forms["signup"]["mail"].value;
	var atpos=x.indexOf("@");
	var dotpos=x.lastIndexOf(".");
	if (atpos<1 || dotpos<atpos+2 || dotpos+2>=x.length)
	{
		alert("Missing or not a valid email address");
		return false;
	}
}
