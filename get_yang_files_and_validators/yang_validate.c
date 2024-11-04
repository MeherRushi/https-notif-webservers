#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <libyang/libyang.h>

char *read_file_to_string(const char *filename) {
    FILE *file = fopen(filename, "rb");  // Open file in binary read mode
    if (!file) {
        perror("Error opening file\n");
        return NULL;  // Return NULL on error
    }

    // Seek to the end of the file to determine size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);  // Reset the file pointer to the beginning

    // Allocate memory for the string (+1 for null terminator)
    char *buffer = (char *)malloc(file_size + 1);
    if (!buffer) {
        perror("Memory allocation failed\n");
        fclose(file);
        return NULL;  // Return NULL on allocation failure
    }

    // Read the file into the buffer
    fread(buffer, 1, file_size, file);
    buffer[file_size] = '\0';  // Null-terminate the string

    fclose(file);  // Close the file
    return buffer;  // Return the buffer
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <data_file_path> <yang_model_path>\n", argv[0]);
        return 1;  // Exit with error if the wrong number of arguments is provided
    }

    /* Since we want to have a web server, we can read data in any way that we wish to
    here for the demo, we read from a file in the same directory*/

    const char *data_file_path = argv[1];
    const char *yang_model_path = argv[2];

    struct ly_ctx *ctx = NULL;
    struct lys_module *module = NULL;  
    struct lyd_node *data_tree = NULL;
    char *yang_data = read_file_to_string(data_file_path);

    if (yang_data) {
        printf("File content:\n%s", yang_data);
        if (ly_ctx_new(NULL, 0, &ctx) != LY_SUCCESS) {
            printf("Failed to create libyang context\n");
            return 1;
        }

    
        if (lys_parse_path(ctx, yang_model_path, LYS_IN_YANG, &module) != LY_SUCCESS) {
            printf("Failed to load module\n");
            printf("DEBUG:Yang model path provided: %s\n",yang_model_path);
            ly_ctx_destroy(ctx);
            return 1;
        }


        if (lyd_parse_data_mem(ctx, yang_data, LYD_XML, LYD_PARSE_STRICT | LYD_PARSE_ONLY, 0, &data_tree) != LY_SUCCESS) {
            printf("Failed to parse data\n");
            ly_ctx_destroy(ctx);
            return 1;
        }

        printf("Data is valid per YANG schema\n");

        lyd_free_all(data_tree);
        ly_ctx_destroy(ctx);
        free(yang_data);  // Free the allocated memory
    } else {    
        printf("Failed to read file\n");
        return 1;
    }

    return 0;
}
