
//--JavaScript function shows or hides your history section
function toggleHistory() { // function created 
    const historySection = document.getElementById("historySection");
     // when  we click on this button from htlm this function runs
    historySection.classList.toggle("show");
    // this add or remove css class when you click   on it 
    
}

function confirmDelete() {
    return confirm("Are you sure you want to delete this history item?");
}