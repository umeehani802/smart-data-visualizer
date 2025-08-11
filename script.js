function uploadFile() {
  const input = document.getElementById('csvFile');
  const file = input.files[0];

  if (!file) {
    alert('Please upload a CSV file first.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById('summary').textContent = JSON.stringify(data.summary, null, 2);
     document.getElementById('histogram').src = '/' + data.histogram;
document.getElementById('heatmap').src = '/' + data.heatmap;

    })
    .catch(err => {
      alert('Error occurred while uploading file.');
      console.error(err);
    });
}
