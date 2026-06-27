```powershell
# For the AVR (Arduino) architecture:
winget install -e --id ZakKemble.avr-gcc

# For the ARM Cortex architecture:
winget install -e --id Arm.GnuArmEmbeddedToolchain

```

* **`ZakKemble.avr-gcc`**: This is the recognized, actively maintained open-source distribution of the AVR toolchain in the `winget` repository.
* **`Arm.GnuArmEmbeddedToolchain`**: This is the official package ID for the GNU ARM compiler.

You are exactly right. The `.hex` file is the universal passport.

Once a `.hex` file is generated, the simulators (both SimulIDE and PICSimLab) do not care how it was made, what IDE you used, or what text editor you typed in. Your only goal in a sovereign workspace is to generate that `.hex` file as cleanly and quickly as possible.

However, here is the critical reality check: **You cannot use the `avr-gcc` or `arm-none-eabi` compilers for PIC microcontrollers.** PIC chips use a highly proprietary memory architecture. To compile code for a PIC, you must use Microchip's official compiler. But we can bypass the 1.1GB MPLAB IDE bloatware completely.

Here is the exact, high-velocity blueprint to compile and simulate across multiple different microcontroller families using only VS Code and your terminal.

---

### Phase 1: The Missing Engine (Standalone XC8)

To work with 8-bit PICs (like the PIC16 and PIC18 families heavily featured in PICSimLab tutorials), you need the standalone XC8 compiler.

1. Go to the Microchip Compilers page.
2. Download the **MPLAB XC8 Compiler** (Standalone).
3. The download size is **~120MB**, keeping it safely below heavy storage thresholds.
4. Run the installer and **ensure you check the box that says "Add XC8 to system PATH."**

---

### Phase 2: Multi-Board Execution Steps (The Layman Guide)

Here is how you handle the workflow for two completely different boards inside PICSimLab, proving that the `.hex` file is the only thing that matters.

#### Board 1: The PIC16F887 (Using the PICSimLab "McLab2" Board)

This is the classic PIC learning board.

**1. The Code (`main.c`)**
Create a folder for your PIC project and save this simple blinking LED code:

```c
#include <xc.h>

// Configuration bits (required for PIC chips to set the internal clock)
#pragma config FOSC = INTRC_NOCLKOUT
#pragma config WDTE = OFF

#define _XTAL_FREQ 4000000 // 4MHz internal clock

void main(void) {
    TRISD = 0x00; // Set all PORTD pins as outputs (where LEDs are usually connected)
    PORTD = 0x00; // Turn off all LEDs

    while(1) {
        PORTD = 0xFF; // Turn ON all PORTD LEDs
        __delay_ms(500);
        PORTD = 0x00; // Turn OFF
        __delay_ms(500);
    }
}

```

**2. The Terminal Command**
Open your VS Code terminal in that folder and run the XC8 compiler directly:

```powershell
xc8-cc -mcpu=16F887 -O2 main.c -o firmware.hex

```

*This instantly generates `firmware.hex` in your directory.*

**3. The Simulator Execution**

1. Open **PICSimLab**.
2. Click **Board** -> **McLab2** (This board has a PIC16F887 socket).
3. Click **Microcontroller** -> **PIC16F887**.
4. Click **File** -> **Load Hex** -> Select your `firmware.hex`.
*Result: The virtual LEDs on the McLab2 board will start blinking.*

---

#### Board 2: The Arduino Uno (Using the PICSimLab "Arduino Uno" Board)

If a tutorial calls for an Arduino (which uses the ATmega328P chip), you switch to the `avr-gcc` compiler you already installed.

**1. The Code (`main.c`)**
Create a new folder and save this bare-metal AVR code:

```c
#define F_CPU 16000000UL // 16MHz Arduino Clock
#include <avr/io.h>
#include <util/delay.h>

int main(void) {
    DDRB |= (1 << DDB5); // Set Pin 13 (Port B, Pin 5) as output

    while (1) {
        PORTB |= (1 << PORTB5); // Turn LED ON
        _delay_ms(500);
        PORTB &= ~(1 << PORTB5); // Turn LED OFF
        _delay_ms(500);
    }
}

```

**2. The Terminal Command**
Because AVR compilation requires a two-step extraction to get the hex, you run this in your terminal:

```powershell
avr-gcc -mmcu=atmega328p -Os main.c -o firmware.elf
avr-objcopy -O ihex -R .eeprom firmware.elf firmware.hex

```

*This outputs a clean `firmware.hex` ready for the Arduino.*

**3. The Simulator Execution**

1. Open **PICSimLab**.
2. Click **Board** -> **Arduino Uno**.
3. Click **Microcontroller** -> **ATmega328P**.
4. Click **File** -> **Load Hex** -> Select your new `firmware.hex`.
*Result: The built-in LED (Pin 13) on the virtual Arduino board will blink.*

---

### Phase 3: The Universal Orchestrator

Typing those commands manually every time you change a line of code creates friction. To optimize your workflow for high-velocity engineering, you create a standard batch script (`build.bat`) in your project folder.

If you are working on a PIC project, your `build.bat` looks exactly like this:

```bat
@echo off
echo Compiling PIC Firmware...
xc8-cc -mcpu=16F887 -O2 main.c -o firmware.hex

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Restarting Simulator...
    taskkill /F /IM picsimlab.exe 2>nul
    start "" "C:\Path\To\PICSimLab\picsimlab.exe" firmware.hex
) else (
    echo Build Failed! Check syntax.
)

```

### The ARM Reality Check (The Missing File)

For ARM-based boards inside PICSimLab (such as the simulated **STM32 Blue Pill** board running a `stm32f103c8t6`), you cannot use a simple single-file execution loop like you do with an 8-bit AVR or PIC.

Unlike 8-bit chips, 32-bit ARM Cortex-M microcontrollers have a complex memory map, flash vectors, and clock configuration layouts. They require an explicit **Startup Assembly file**, a dedicated **Linker Script (`.ld`)**, and **System Header definitions** alongside your core `main.c` function. Without these, the hardware emulator won't know where the initial stack pointer is located or where the execution memory vector array begins.

---

### The Sovereign CMake Orchestration Architecture

Rather than dealing with massive IDEs, use a clean **CMake** build pattern to compile and link these components entirely through your terminal.

Below is the complete project directory structure and code configuration to compile a working raw binary format (`.bin` or `.hex`) for the virtual Blue Pill board using your `Arm.GnuArmEmbeddedToolchain` environment.

#### 1. Project Directory Layout

```text
my_arm_project/
├── CMakeLists.txt
├── link.ld
├── startup.s
└── main.c

```

#### 2. The Linker Memory Setup (`link.ld`)

This informs the compiler backend exactly where the ROM and RAM barriers live inside the virtual STM32 silicon.

```linker
MEMORY
{
    FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 64K
    RAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 20K
}

SECTIONS
{
    .text : {
        KEEP(*(.isr_vector))
        *(.text*)
        *(.rodata*)
    } > FLASH

    .data : {
        *(.data*)
    } > RAM AT > FLASH

    .bss : {
        *(.bss*)
    } > RAM
}

```

#### 3. The Core Execution Entry (`main.c`)

This manipulates the raw registers directly to configure the Reset and Clock Control (RCC) block and toggle port pin C13 (the standard onboard status LED on the Blue Pill board).

```c
#include <stdint.h>

// Microcontroller hardware register definition shortcuts
#define RCC_BASE      0x40021000
#define RCC_APB2ENR   (*(volatile uint32_t *)(RCC_BASE + 0x18))

#define GPIOC_BASE    0x40011000
#define GPIOC_CRH     (*(volatile uint32_t *)(GPIOC_BASE + 0x04))
#define GPIOC_ODR     (*(volatile uint32_t *)(GPIOC_BASE + 0x0C))

void delay(volatile uint32_t count) {
    while (count--) {
        __asm__("nop");
    }
}

int main(void) {
    // 1. Energize the internal bus clock tracking for Port C
    RCC_APB2ENR |= (1 << 4);

    // 2. Configure Pin 13 as a standard push-pull digital output
    GPIOC_CRH &= ~(0xF << 20); 
    GPIOC_CRH |= (0x2 << 20);  

    while (1) {
        GPIOC_ODR &= ~(1 << 13); // Pull Pin Low (LED turns ON)
        delay(300000);
        GPIOC_ODR |= (1 << 13);  // Pull Pin High (LED turns OFF)
        delay(300000);
    }
}

```

#### 4. The Interrupt Vector Engine (`startup.s`)

This basic assembly file defines the foundational vector table layout that points straight to your `main` function loop immediately upon hardware initialization.

```assembly
.syntax unified
.cpu cortex-m3
.thumb

.global g_pfnVectors
.global Reset_Handler

.section .isr_vector,"a",%progbits
g_pfnVectors:
    .word 0x20005000         /* Top of Stack allocation boundary */
    .word Reset_Handler      /* The fundamental hardware entry execution vector */

.section .text.Reset_Handler
Reset_Handler:
    bl main
    b .

```

#### 5. The Master Orchestrator Blueprint (`CMakeLists.txt`)

```cmake
cmake_minimum_required(VERSION 3.15)

project(STM32_Sovereign_Blink C ASM)

# Force the project to use the ARM cross-compiler flags directly
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(CMAKE_C_COMPILER arm-none-eabi-gcc)
set(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
set(CMAKE_OBJCOPY arm-none-eabi-objcopy)

# Bare-metal compile targets optimization settings
set(CMAKE_C_FLAGS "-mcpu=cortex-m3 -mthumb -O2 -ffunction-sections -fdata-sections -nostdlib" CACHE INTERNAL "")
set(CMAKE_ASM_FLAGS "-mcpu=cortex-m3 -mthumb" CACHE INTERNAL "")
set(CMAKE_EXE_LINKER_FLAGS "-T ${CMAKE_CURRENT_SOURCE_DIR}/link.ld -Wl,--gc-sections" CACHE INTERNAL "")

# Define target workspace outputs
add_executable(${PROJECT_NAME}.elf main.c startup.s)

# Post-build translation macro step to extract raw binaries
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary ${PROJECT_NAME}.elf ${PROJECT_NAME}.bin
    COMMENT "Extracting raw deployment binary file: ${PROJECT_NAME}.bin"
)

```

---

### Step-by-Step Compilation & Deployment Strategy

To execute this entire build process locally, open your VS Code terminal within your project directory and run the following terminal sequence:

```powershell
# Create an isolated build workspace cache folder
mkdir build
cd build

# Initialize and configure the system tracking engine via CMake
cmake ..

# Run the compilation sequence to generate the target file
cmake --build .

```

#### Running it in PICSimLab:

1. Open **PICSimLab**.
2. Go to **Board** -> Select **Blue_Pill**.
3. Go to **Microcontroller** -> Select **stm32f103c8t6**.
4. Click **File** -> **Load Hex** -> Navigate to your `build` directory and select **`STM32_Sovereign_Blink.bin`**


## Dealing with Microchip Device Packs

The article you provided notes that Microchip distributes definitions as device packs. When you download a modern standalone compiler or a toolchain like the one above, the core device definitions for classic chips (ATmega328P, ATmega2560) are already baked into the compiler's include directory.

However, if you ever compile for a brand-new or obscure chip and get a device not recognized error, you don't need the MPLAB IDE. You can download the standalone pack directly from packs.download.microchip.com.

## When Winget goes missing

### Direct execution bypassing the PATH tracking variable

& "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\winget.exe" --version

#### Fix corrupted user-level Path environment variable settings in the registry

& {
    param($key)
    $currentPath = Get-ItemPropertyValue $key Path
    # Ensure the standard WindowsApps location is explicitly pinned
    $targetAppPath = "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"
    if ($currentPath -notlike "*$targetAppPath*") {
        Set-ItemProperty -Type ExpandString $key Path "$currentPath;$targetAppPath"
        Write-Host "Injected local app path wrapper back into user space."
    }
} registry::HKEY_CURRENT_USER\Environment

#### Force Windows Explorer to instantly reload environment caches without logging out

Stop-Process -Name explorer -Force

