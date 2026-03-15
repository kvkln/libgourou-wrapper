// Files stay in the fileinput when reloading; add them to the list again
window.addEventListener('load', function() {
    const fileinput = document.getElementById('fileinput');
    appendFilesToFileList(fileinput.files);
});

function dragoverHandler(ev) {
    ev.preventDefault();
    ev.dataTransfer.dropEffect = 'move';
}

function dropHandler(ev) {
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();

    if (ev.dataTransfer.files.length !== 0) {
        const fileinput = document.getElementById('fileinput');
        const dt = new DataTransfer();

        for (const file of fileinput.files) {
            dt.items.add(file);
        }

        const acsmFiles = [];
        for (const file of ev.dataTransfer.files) {
            if (file.name.toLowerCase().endsWith('.acsm')) {
                acsmFiles.push(file);
                dt.items.add(file);
            }
        }

        fileinput.files = dt.files;
        appendFilesToFileList(acsmFiles);
    }
}

function appendFilesToFileList(files) {
    const filelist = document.getElementById('filelist');
    for (const file of files) {
        const span = document.createElement('span');
        span.innerText = file.name;
        filelist.appendChild(span);
    }
}

function submit() {
    const input = document.getElementById('fileinput');
    if (input.files.length === 0) return;

    const submitButton = document.getElementById('submit-btn');
    submitButton.classList.toggle('loading', true);
    let pending = input.files.length;

    for (const file of input.files) {
        const formData = new FormData();
        formData.append('file', file);

        let filename = 'book.epub';

        fetch('/convert', {
            method: 'post',
            body: formData,
        })
        .then(async res => {
            if (res.ok) {
                const disposition = res.headers.get('content-disposition');
                filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
                if (filename.toLowerCase().startsWith("utf-8''")) {
                    filename = decodeURIComponent(filename.replace(/utf-8''/i, ''));
                } else {
                    filename = filename.replace(/['"]/g, '');
                }
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert('Error: ' + await res.text());
            }
        })
        .catch(err => {
            alert('Error: ' + err.message);
        })
        .finally(() => {
            pending -= 1;
            if (pending === 0) {
                submitButton.classList.toggle('loading', false);
            }
        });
    }
}

function clearFiles() {
    const input = document.getElementById('fileinput');
    input.value = '';
    const filelist = document.getElementById('filelist');
    filelist.innerHTML = '';
}
