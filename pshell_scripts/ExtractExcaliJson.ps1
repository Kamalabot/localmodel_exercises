Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Excalidraw Text Extractor" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "1. Go to Excalidraw."
Write-Host "2. Select your text blocks/shapes and press Ctrl+C."
Write-Host ""
Read-Host "-> Once you have copied the content, press ENTER to extract"
Write-Host "----------------------------------------------------------"

$clipboardContent = Get-Clipboard -Raw

if ([string]::IsNullOrWhiteSpace($clipboardContent)) {
    Write-Error "Action Failed: Clipboard buffer is empty."
    exit
}

try {
    $parsedObj = ConvertFrom-Json $clipboardContent -ErrorAction Stop
} catch {
    Write-Error "Action Failed: Clipboard content is not valid JSON."
    exit
}

if (-not $parsedObj.elements) {
    Write-Error "Action Failed: Valid JSON found, but it lacks Excalidraw canvas metadata."
    exit
}

$textBlocks = $parsedObj.elements | 
    Where-Object { $_.type -eq "text" -and -not $_.isDeleted } | 
    Sort-Object y

if ($textBlocks.Count -eq 0) {
    Write-Warning "No active text elements discovered in the parsed canvas payload."
    exit
}

Write-Host ""
Write-Host "--- EXTRACTED BLOCKS (TOP TO BOTTOM) ---" -ForegroundColor Green
foreach ($block in $textBlocks) {
    Write-Output $block.text
    Write-Output "----------------------------------------"
}