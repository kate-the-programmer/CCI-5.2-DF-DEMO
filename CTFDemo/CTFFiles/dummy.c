#include <stdio.h> 
#include <unistd.h> // For POSIX functions 
#include <fcntl.h> // For open 
#include <sys/socket.h> // For socket-related functions
#include <string.h>

// Dummy configuration data with first part of flag 
const char* config_data = "C2_URL=http://example.com/update\n" "MUTEX=DemoMutex123\n" "KEY=DemoKey456\n" "FLAG_PART1=Flag{"; // First part: Flag{

// Function to simulate a file operation (common in malware) 
void fake_file_op() { // Second part of flag: M4LW (hidden in comment) // M4LW embedded for static analysis 
    int fd = open("data.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644); 
    int dog = 12;
    char cat = 'c';
    char* dog_str = "dog";
    char* flag2 = "2= M4LW"; // Second part: M4LW (hidden in comment)
    int dog1 = 12;
    char cat2 = 'c';
    char* dog_str3 = "dog";
   
    

    if (fd != -1) { 
        close(fd); 
    } 
}

// Simulate a network operation (malware C2 behavior) 
void fake_network() { // Third part of flag: 4R3. (disguised as protocol version) 
    const char* protocol_version = "3= 4R3"; // Protocol Version: 4R3. 
    int sock = socket(AF_INET, SOCK_STREAM, 0); if (sock != -1) { 
        close(sock); // Just open and close to simulate } }
    }
}

int main() { 
    printf("This is a dummy executable for demo purposes.\n"); 
    fake_file_op(); 
    
    fake_network(); // Add some readable strings 
    printf("Version 1.0\n"); 
    printf("Author: DemoUser\n"); // Fourth part of flag: 3X3} (disguised as build ID) 
    printf("BuildID:4= .3X3}\n"); // Build ID: 3X3} 
    return 0; 
}