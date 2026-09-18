# Принимаем путь из реестра (переменная %V)
param(
    [string]$TargetPath
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Транслитерация
function Convert-ToTranslit {
    param([string]$text)
    $map = @{
        'а'='a';'б'='b';'в'='v';'г'='g';'д'='d';'е'='e';'ё'='yo';'ж'='zh';'з'='z';'и'='i';'й'='y';'к'='k';'л'='l';'м'='m';'н'='n';'о'='o';'п'='p';'р'='r';'с'='s';'т'='t';'у'='u';'ф'='f';'х'='kh';'ц'='ts';'ч'='ch';'ш'='sh';'щ'='shch';'ъ'='';'ы'='y';'ь'='';'э'='e';'ю'='yu';'я'='ya'
        'А'='A';'Б'='B';'В'='V';'Г'='G';'Д'='D';'Е'='E';'Ё'='Yo';'Ж'='Zh';'З'='Z';'И'='I';'Й'='Y';'К'='K';'Л'='L';'М'='M';'Н'='N';'О'='O';'П'='P';'Р'='R';'С'='S';'Т'='T';'У'='U';'Ф'='F';'Х'='Kh';'Ц'='Ts';'Ч'='Ch';'Ш'='Sh';'Щ'='Shch';'Ъ'='';'Ы'='Y';'Ь'='';'Э'='E';'Ю'='Yu';'Я'='Ya'
    }
    $result = ""
    foreach ($c in $text.ToCharArray()) { $result += if ($map.ContainsKey($c)) { $map[$c] } else { $c } }
    return $result
}

# Диалог ввода
function Show-InputBox {
    param([string]$prompt, [string]$title, [string]$defaultValue = "")
    $form = New-Object System.Windows.Forms.Form
    $form.Text = $title
    $form.Size = New-Object System.Drawing.Size(400, 150)
    $form.StartPosition = 'CenterScreen'
    $form.FormBorderStyle = 'FixedDialog'
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $label = New-Object System.Windows.Forms.Label
    $label.Text = $prompt
    $label.Location = New-Object System.Drawing.Point(10, 20)
    $label.Size = New-Object System.Drawing.Size(360, 20)
    $form.Controls.Add($label)
    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Location = New-Object System.Drawing.Point(10, 50)
    $textBox.Size = New-Object System.Drawing.Size(360, 20)
    $textBox.Text = $defaultValue
    $form.Controls.Add($textBox)
    $button = New-Object System.Windows.Forms.Button
    $button.Text = 'OK'
    $button.Location = New-Object System.Drawing.Point(150, 80)
    $button.Size = New-Object System.Drawing.Size(75, 25)
    $button.Add_Click({ $form.DialogResult = 'OK'; $form.Close() })
    $form.Controls.Add($button)
    $form.AcceptButton = $button
    if ($form.ShowDialog() -eq 'OK') { return $textBox.Text } else { return $null }
}

# --- Основная часть ---

# Если путь не передан (например, запуск вручную), берём текущую папку
if (-not $TargetPath) {
    $TargetPath = (Get-Location).Path
}

# Проверяем, что папка существует
if (-not (Test-Path -Path $TargetPath -PathType Container)) {
    [System.Windows.Forms.MessageBox]::Show("Папка не найдена: $TargetPath", "Ошибка", 'OK', 'Error')
    exit 1
}

$number = Show-InputBox -prompt "Введите номер (например, 0001):" -title "Номер папки"
if ($number -eq $null) { exit }

$companyName = Show-InputBox -prompt "Введите название компании:" -title "Название компании"
if ($companyName -eq $null) { exit }

$translitName = Convert-ToTranslit -text $companyName
$folderName = "zak_$number`_$translitName"
$fullPath = Join-Path -Path $TargetPath -ChildPath $folderName

try {
    New-Item -Path $fullPath -ItemType Directory -ErrorAction Stop
    [System.Windows.Forms.MessageBox]::Show("Папка создана: $folderName", "Успех", 'OK', 'Information')
} catch {
    [System.Windows.Forms.MessageBox]::Show("Ошибка: $_", "Ошибка", 'OK', 'Error')
}