param([int]$Start = 0, [int]$Count = 12)

$root = 'E:\Study\Programs\AI Agent Demo'
$node = 'E:\DeepSeek\dsh-home\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe'
$py   = 'E:\DeepSeek\dsh-home\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$dstDir = Join-Path $root 'data\tenants\demo\fault_codes'

function Get-DocType([string]$slug) {
  if ($slug -match '^(how-to-enter|version-ams|ams-led-status)') { return 'manual' }
  if ($slug -match '^(enable-the-video|export-failed-print-log|update-log-to-a-ticket)') { return 'process' }
  return 'fault_code'
}

$links = Get-Content (Join-Path $root 'tmp_links.json') -Raw | ConvertFrom-Json
$existing = (Import-Csv (Join-Path $root 'corpus.csv') -Encoding UTF8).source_url
$todo = @($links | Where-Object { $existing -notcontains $_.href })
"待处理: $($todo.Count) 条；本次取 $Start 起 $Count 条"

$todo | Select-Object -Skip $Start -First $Count | ForEach-Object {
  $href = $_.href
  $slug = ($href -split '/')[-1]
  $file = "X1_fault_code_v1.0_$slug.md"
  $tmp  = Join-Path $root ("tmp_" + $file)
  $dst  = Join-Path $dstDir $file

  Push-Location (Join-Path $root 'tools\wiki2md')
  & $node convert.mjs $href $tmp | Out-Null
  $ok = ($LASTEXITCODE -eq 0) -and (Test-Path -LiteralPath $tmp)
  Pop-Location

  if (-not $ok) { "FAIL convert: $slug"; return }

  $chars = (Get-Content -LiteralPath $tmp -Raw).Length
  if ($chars -lt 200) { "SKIP too short ($chars): $slug"; Remove-Item -LiteralPath $tmp -Force; return }

  Move-Item -LiteralPath $tmp -Destination $dst -Force
  $tline = (Select-String -LiteralPath $dst -Pattern '^title: ' | Select-Object -First 1).Line
  $title = ($tline -replace '^title:\s*', '' -replace '\s*\|\s*Bambu Lab Wiki\s*$', '').Trim()
  $docType = Get-DocType $slug

  Push-Location $root
  & $py scripts\add_corpus.py --file ("data/tenants/demo/fault_codes/" + $file) `
      --title $title --model 'X1|P1' --doc-type $docType --version '2026-10-26' `
      --source-url $href --license '可转载·禁止商用' --notes 'X1 故障排除索引页收录' | Out-Null
  Pop-Location

  "OK ($chars): $slug -> $docType"
}
