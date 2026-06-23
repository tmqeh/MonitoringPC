@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo  DBA 계정 암호 변경 스크립트
echo ============================================
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [오류] 관리자 권한으로 실행해주세요.
    pause
    exit /b 1
)

:: ============================================
:: STEP 1. 로컬 보안정책 완화 (암호 정책 변경)
:: ============================================
echo [1단계] 로컬 보안정책 완화 중...

net accounts /uniquepw:0
if %errorLevel% neq 0 goto :error

net accounts /minpwlen:0
if %errorLevel% neq 0 goto :error

net accounts /minpwage:0
if %errorLevel% neq 0 goto :error

echo       완료: 최근 암호 기억=0, 최소 길이=0, 최소 사용기간=0일
echo.

:: ============================================
:: STEP 2. 사용자 계정 암호 변경 (우회 후 복구)
:: ============================================
echo [2단계] dba 계정 암호 변경 중...

:: 기존 암호 -> 중간 암호로 변경
net user dba Tltmxpa34!
if %errorLevel% neq 0 (
    echo [오류] 중간 암호 변경 실패. dba 계정을 확인해주세요.
    goto :restore
)
echo       완료: 중간 암호(Tltmxpa34!) 설정

:: 중간 암호 -> 원래 암호로 변경
net user dba Tltmxpa12!
if %errorLevel% neq 0 (
    echo [오류] 최종 암호 복구 실패.
    goto :restore
)
echo       완료: 원래 암호(Tltmxpa12!) 복구
echo.

:: ============================================
:: STEP 3. 로컬 보안정책 원복
:: ============================================
:restore
echo [3단계] 로컬 보안정책 원복 중...

net accounts /uniquepw:5
net accounts /minpwlen:9
net accounts /minpwage:1

echo       완료: 최근 암호 기억=5, 최소 길이=9, 최소 사용기간=1일
echo.

echo ============================================
echo  모든 작업이 완료되었습니다.
echo ============================================
goto :end

:error
echo [오류] 정책 변경 중 오류가 발생했습니다. 원복을 시도합니다.
goto :restore

:end
echo.
pause
endlocal