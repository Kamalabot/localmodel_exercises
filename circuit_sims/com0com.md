The `command>` prompt you see is the **native interface for `com0com**` [1.1.2]. It is not a standard Windows command prompt; it is a specialized shell for interacting directly with the kernel-mode driver to create and configure your virtual serial ports [1.1.1, 1.1.2].

### How to use the `com0com` Command Prompt

When you see `command>`, you can type the following commands to create and rename your ports [1.1.2].

#### 1. Create a New Pair

To create a new pair of linked ports (e.g., `CNCA0` and `CNCB0`), simply type:

```text
command> install

```

*This will create the virtual devices and display their system names (usually `CNCA0` and `CNCB0`) [1.1.2].*

#### 2. Rename Ports to Standard COM Names

Windows applications often look specifically for "COM" ports (e.g., `COM3`, `COM4`) [1.2.3]. To rename the default ports to something your IDE/simulator can easily recognize:

```text
command> change CNCA0 PortName=COM10
command> change CNCB0 PortName=COM11

```

*(You can use any number that isn't already taken by physical hardware.)*

#### 3. Enable Baud Rate Emulation

To ensure that software on both sides of the "cable" stays synced without errors, it is best practice to enable baud rate emulation [1.1.2, 1.1.3]:

```text
command> change CNCA0 EmuBR=yes
command> change CNCB0 EmuBR=yes

```

#### 4. Verify/List Ports

To see the current configuration or ports you have created:

```text
command> list

```

---

### Important Tips for 2026

* **Driver Signing:** Since you are on a modern Windows system, **driver signature enforcement** is likely active [1.1.1, 1.3.2]. If you have trouble getting the ports to appear or function, ensure you downloaded a **signed version** of the driver (version 2.2.2.0 is the most commonly cited "stable/signed" version for compatibility) [1.2.2, 1.2.3, 1.3.2].
* **No Device Manager Entry:** A common point of confusion is that these virtual ports **do not appear** in the standard "Ports (COM & LPT)" section of Windows Device Manager [1.3.2]. They are handled directly by the `com0com` driver. Your applications (SimulIDE, PICSimLab, VS Code) will still see them as valid COM ports if you manually type the name (e.g., `COM10`) into the connection settings [1.3.2].
* **Flow Control:** When configuring your applications to connect to these ports, always ensure **"No Flow Control"** is selected in the port settings, otherwise, the virtual link may hang [1.2.2].