# Definindo variáveis de ambiente
Write-Output "Setting environment variables"
$env:IN_DEBUGGER = $true

# Executando os testes
Write-Output "Running tests"
pytest --disable-warnings
