param([string]$TargetPath)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Convert-ToTranslit {
    param([string]$text)
    $lowerRu  = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    $lowerLat = 'abvgdeezhziyklmnoprstufhtschshshhyyeyuya'
    $upperRu  = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    $upperLat = 'ABVGDEEZHZIYKLMNOPRSTUFHTSSHCHSHHYEYUYA'
    
    $map = @{}
    for ($i=0; $i -lt $lowerRu.Length; $i++) {
        $map[$lowerRu[$i]] = $lowerLat[$i]
        $map[$upperRu[$i]] = $upperLat[$i]
    }
    $result = ''
    foreach ($c in $text.ToCharArray()) {
        $result += if ($map.ContainsKey($c)) { $map[$c] } else { $c }
    }
    return $result
}

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

if (-not $TargetPath) { $TargetPath = (Get-Location).Path }
if (-not (Test-Path -Path $TargetPath -PathType Container)) {
    [System.Windows.Forms.MessageBox]::Show("Папка не найдена: $TargetPath", "Ошибка", 'OK', 'Error')
    exit 1
}

$number = Show-InputBox -prompt "Введите номер (например, 0001):" -title "Номер папки"
if ($number -eq $null) { exit }

$company = Show-InputBox -prompt "Введите название компании:" -title "Название компании"
if ($company -eq $null) { exit }

$translit = Convert-ToTranslit -text $company
$folderName = "zak_$number`_$translit"
$fullPath = Join-Path -Path $TargetPath -ChildPath $folderName

try {
    New-Item -Path $fullPath -ItemType Directory -ErrorAction Stop
    [System.Windows.Forms.MessageBox]::Show("Папка создана: $folderName", "Успех", 'OK', 'Information')
} catch {
    [System.Windows.Forms.MessageBox]::Show("Ошибка: $_", "Ошибка", 'OK', 'Error')
}