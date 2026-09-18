# Загружаем сборку для графического диалога
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Функция транслитерации с русского на латиницу
function Convert-ToTranslit {
    param([string]$text)
    
    $translitMap = @{
        'а' = 'a'; 'б' = 'b'; 'в' = 'v'; 'г' = 'g'; 'д' = 'd'; 'е' = 'e'; 'ё' = 'yo'
        'ж' = 'zh'; 'з' = 'z'; 'и' = 'i'; 'й' = 'y'; 'к' = 'k'; 'л' = 'l'; 'м' = 'm'
        'н' = 'n'; 'о' = 'o'; 'п' = 'p'; 'р' = 'r'; 'с' = 's'; 'т' = 't'; 'у' = 'u'
        'ф' = 'f'; 'х' = 'kh'; 'ц' = 'ts'; 'ч' = 'ch'; 'ш' = 'sh'; 'щ' = 'shch'
        'ъ' = ''; 'ы' = 'y'; 'ь' = ''; 'э' = 'e'; 'ю' = 'yu'; 'я' = 'ya'
        'А' = 'A'; 'Б' = 'B'; 'В' = 'V'; 'Г' = 'G'; 'Д' = 'D'; 'Е' = 'E'; 'Ё' = 'Yo'
        'Ж' = 'Zh'; 'З' = 'Z'; 'И' = 'I'; 'Й' = 'Y'; 'К' = 'K'; 'Л' = 'L'; 'М' = 'M'
        'Н' = 'N'; 'О' = 'O'; 'П' = 'P'; 'Р' = 'R'; 'С' = 'S'; 'Т' = 'T'; 'У' = 'U'
        'Ф' = 'F'; 'Х' = 'Kh'; 'Ц' = 'Ts'; 'Ч' = 'Ch'; 'Ш' = 'Sh'; 'Щ' = 'Shch'
        'Ъ' = ''; 'Ы' = 'Y'; 'Ь' = ''; 'Э' = 'E'; 'Ю' = 'Yu'; 'Я' = 'Ya'
    }
    
    $result = ""
    foreach ($char in $text.ToCharArray()) {
        if ($translitMap.ContainsKey($char)) {
            $result += $translitMap[$char]
        } else {
            # Если символ не найден в карте (например, латиница или цифры), оставляем как есть
            $result += $char
        }
    }
    return $result
}

# Функция для отображения диалогового окна ввода
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
    $result = $form.ShowDialog()
    
    if ($result -eq 'OK') {
        return $textBox.Text
    } else {
        return $null
    }
}

# --- Основная часть скрипта ---

# Получаем текущую папку (откуда был вызван скрипт)
$currentPath = (Get-Location).Path

# Запрашиваем номер
$number = Show-InputBox -prompt "Введите номер (например, 0001):" -title "Номер папки"
if ($number -eq $null) { exit }

# Запрашиваем название компании
$companyName = Show-InputBox -prompt "Введите название компании:" -title "Название компании"
if ($companyName -eq $null) { exit }

# Транслитерируем название
$transliteratedName = Convert-ToTranslit -text $companyName

# Формируем имя папки: zak_XXXX_Name
$folderName = "zak_$number`_$transliteratedName"

# Создаем папку
$fullPath = Join-Path -Path $currentPath -ChildPath $folderName
try {
    New-Item -Path $fullPath -ItemType Directory -ErrorAction Stop
    Write-Host "Папка успешно создана: $fullPath"
} catch {
    [System.Windows.Forms.MessageBox]::Show("Ошибка при создании папки: $_", "Ошибка", 'OK', 'Error')
}