#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <libyang/libyang.h>


int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <data> <ietf_yang_model_path> <example_yang_model_path>\n", argv[0]);
        return 1;
    }

    char *yang_data = argv[1];
    const char *ietf_yang_model_path = argv[2];
    const char *example_yang_model_path = argv[3];

    struct ly_ctx *ctx = NULL;
    struct lys_module *ietf_module = NULL;
    struct lys_module *example_module = NULL;
    struct lyd_node *data_tree = NULL;

    if (yang_data) {
        printf("File content:\n%s", yang_data);
        
        if (ly_ctx_new(NULL, 0, &ctx) != LY_SUCCESS) {
            printf("Failed to create libyang context\n");
            return 1;
        }

        // Load the ietf-notification.yang module
        if (lys_parse_path(ctx, ietf_yang_model_path, LYS_IN_YANG, &ietf_module) != LY_SUCCESS) {
            printf("Failed to load ietf-notification module\n");
            printf("DEBUG: ietf-notification model path: %s\n", ietf_yang_model_path);
            ly_ctx_destroy(ctx);
            return 1;
        }

        // Load the example-mod.yang module
        if (lys_parse_path(ctx, example_yang_model_path, LYS_IN_YANG, &example_module) != LY_SUCCESS) {
            printf("Failed to load example-mod module\n");
            printf("DEBUG: example-mod model path: %s\n", example_yang_model_path);
            ly_ctx_destroy(ctx);
            return 1;
        }

        // Parse the XML data
        if (lyd_parse_data_mem(ctx, yang_data, LYD_XML, LYD_PARSE_STRICT | LYD_PARSE_ONLY, 0, &data_tree) != LY_SUCCESS) {
            printf("Failed to parse data\n");
            ly_ctx_destroy(ctx);
            return 1;
        }

        printf("Data is valid per YANG schema\n");

        lyd_free_all(data_tree);
        ly_ctx_destroy(ctx);
        free(yang_data);
    } else {
        printf("Failed to read file\n");
        return 1;
    }

    return 0;
}
