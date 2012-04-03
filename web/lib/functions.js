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
