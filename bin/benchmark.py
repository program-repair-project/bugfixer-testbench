benchmark = {
    "gmp": ["13420-13421", "14166-14167"],
    "libtiff": [
        "2005-12-14-6746b87-0d3d51d", "2005-12-21-3b848a7-3edb9cd",
        "2006-02-23-b2ce5d8-207c78a", "2006-03-03-a72cf60-0a36d7f",
        "2007-08-24-827b6bc-22da1d6", "2007-11-02-371336d-865f7b2",
        "2008-12-30-362dee5-565eaa2", "2009-02-05-764dbba-2e42d63",
        "2009-06-30-b44af47-e0b51f3", "2010-11-27-eb326f9-eec7ec0",
        "2010-12-13-96a5fb4-bdba15c"
    ],
    "php": [
        "2011-01-18-95388b7cda-b9b1fb1827",
        "2011-02-21-2a6968e43a-ecb9d8019c",
        "2011-03-11-d890ece3fc-6e74d95f34",
        "2011-03-27-11efb7295e-f7b7b6aa9e",
        "2011-04-07-d3274b7f20-77ed819430",
        "2011-10-31-c4eb5f2387-2e5d5e5ac6",
        "2011-11-08-0ac9b9b0ae-cacf363957",
        "2011-11-08-c3e56a152c-3598185a74",
        "2011-11-11-fcbfbea8d2-c1e510aea8",
        "2011-11-19-eeba0b5681-f330c8ab4e",
        "2011-12-04-1e6a82a1cf-dfa08dc325",
        "2012-03-08-0169020e49-cdc512afb3",
        "2012-03-12-7aefbf70a8-efc94f3115",
    ]
}

bic_location = {
    "libtiff": {
        "2005-12-14-6746b87-0d3d51d": [("tiffcp.c", 746), ("tiffcp.c", 855)],
        "2005-12-21-3b848a7-3edb9cd": [("tif_dirread.c", 590)],
        "2006-02-23-b2ce5d8-207c78a": [("tif_dirwrite.c", 338)],
        "2006-03-03-a72cf60-0a36d7f": [("tif_dirread.c", 976)],
        "2007-08-24-827b6bc-22da1d6": [("tif_dirinfo.c", 333),
                                       ("tif_dirinfo.c", 363)],
        "2007-11-02-371336d-865f7b2": [("tif_dirwrite.c", 346)],
        "2008-12-30-362dee5-565eaa2": [("tif_dirwrite.c", 1677),
                                       ("thumbnail.c", 164),
                                       ("thumbnail.c", 187),
                                       ("thumbnail.c", 558),
                                       ("thumbnail.c", 600)],
        "2009-02-05-764dbba-2e42d63": [("tiffcrop.c", 2690)],
        "2009-06-30-b44af47-e0b51f3":
        [("tiffcp.c", 355)],  # for sparrow else node issue
        "2010-11-27-eb326f9-eec7ec0": [("tiff2pdf.c", 769)],
        "2010-12-13-96a5fb4-bdba15c": [("tiffcrop.c", 1889),
                                       ("tiffcrop.c", 4612),
                                       ("tiffcrop.c", 4614),
                                       ("tiffcrop.c", 4615),
                                       ("tiffcrop.c", 4632)]
    },
    "gmp": {
        "13420-13421": [("powm.c", 150), ("powm.c", 212), ("powm.c", 218),
                        ("powm.c", 220), ("powm.c", 223), ("powm.c", 226),
                        ("powm.c", 231)],
        "14166-14167": [("gcdext.c", 56)]
    },
    "php": {
        "2011-01-18-95388b7cda-b9b1fb1827": [("document.c", 2321),
                                             ("document.c", 2324)],
        "2011-02-21-2a6968e43a-ecb9d8019c": [("json.c", 417)],
        "2011-03-11-d890ece3fc-6e74d95f34": [("url.c", 301)],
        "2011-03-27-11efb7295e-f7b7b6aa9e": [("php_spl.c", 818),
                                             ("php_spl.c", 831),
                                             ("spl_directory.c", 154)],
        "2011-04-07-d3274b7f20-77ed819430": [("spl_array.c", 514)],
        "2011-10-31-c4eb5f2387-2e5d5e5ac6": [("zend_API.c", 1070)],
        "2011-11-08-c3e56a152c-3598185a74":
        [("zend_builtin_functions.c", 848)],
        "2011-11-11-fcbfbea8d2-c1e510aea8": [("spl_directory.c", 1057)],
        "2011-11-19-eeba0b5681-f330c8ab4e": [("phar.c", 1573)],
        "2011-12-04-1e6a82a1cf-dfa08dc325": [("logical_filters.c", 525)],
        "2012-03-08-0169020e49-cdc512afb3": [("streams.c", 213)],
        "2012-03-12-7aefbf70a8-efc94f3115": [("html.c", 1009)],
    }
}

faulty_function = {
    "libtiff": {
        "2005-12-14-6746b87-0d3d51d":
        ["cpContig2ContigByRow", "cpDecodedStrips"],
        "2005-12-21-3b848a7-3edb9cd": ["TIFFReadDirectory"],
        "2006-02-23-b2ce5d8-207c78a": ["_TIFFWriteDirectory"],
        "2006-03-03-a72cf60-0a36d7f": ["TIFFFetchData"],
        "2007-08-24-827b6bc-22da1d6": ["_TIFFMergeFields"],
        "2007-11-02-371336d-865f7b2": ["TIFFWriteDirectorySec"],
        "2008-12-30-362dee5-565eaa2":
        ["TIFFWriteDirectoryTagSubifd", "cpTag", "generateThumbnail"],
        "2009-02-05-764dbba-2e42d63": ["loadImage"],
        "2009-06-30-b44af47-e0b51f3": ["processCompressOptions"],
        "2010-11-27-eb326f9-eec7ec0": ["main"],
        "2010-12-13-96a5fb4-bdba15c": ["main", "getCropOffsets"]
    },
    "gmp": {
        "13420-13421": ["__gmpn_powm"],
        "14166-14167": ["__gmpz_gcdext"]
    },
    "php": {
        "2011-01-18-95388b7cda-b9b1fb1827": ["zif_dom_document_save_html"],
        "2011-02-21-2a6968e43a-ecb9d8019c": ["json_escape_string"],
        "2011-03-11-d890ece3fc-6e74d95f34": ["php_url_parse_ex"],
        "2011-03-27-11efb7295e-f7b7b6aa9e": [
            "construction_wrapper", "construction_wrapper",
            "spl_filesystem_object_new_ex"
        ],
        "2011-04-07-d3274b7f20-77ed819430": ["spl_array_unset_dimension_ex"],
        "2011-10-31-c4eb5f2387-2e5d5e5ac6": ["_object_and_properties_init"],
        "2011-11-08-c3e56a152c-3598185a74": ["is_a_impl"],
        "2011-11-11-fcbfbea8d2-c1e510aea8":
        ["zim_spl_SplFileInfo_getLinkTarget"],
        "2011-11-19-eeba0b5681-f330c8ab4e": ["phar_open_from_fp"],
        "2011-12-04-1e6a82a1cf-dfa08dc325": ["php_filter_validate_email"],
        "2012-03-08-0169020e49-cdc512afb3":
        ["php_stream_display_wrapper_errors"],
        "2012-03-12-7aefbf70a8-efc94f3115": ["traverse_for_entities"]
    }
}

sparrow_custom_option = {
    "php": {
        "2011-01-18-95388b7cda-b9b1fb1827": [
            "-unsound_alloc", "-unsound_const_string", "-unsound_recursion",
            "-unsound_noreturn_function", "-unsound_skip_global_array_init",
            "100", "-top_location", "-max_pre_iter", "2",
            "-keep_unreachable_from", "zif_dom_document_save_html"
        ],
        "2011-02-21-2a6968e43a-ecb9d8019c": [
            "-unsound_alloc", "-unsound_const_string", "-unsound_recursion",
            "-unsound_noreturn_function", "-unsound_skip_global_array_init",
            "100", "-top_location", "-max_pre_iter", "2",
            "-keep_unreachable_from", "php_json_encode"
        ],
        "2011-03-11-d890ece3fc-6e74d95f34": [
            "-unsound_alloc", "-unsound_const_string", "-unsound_recursion",
            "-unsound_noreturn_function", "-unsound_skip_global_array_init",
            "100", "-top_location", "-max_pre_iter", "2",
            "-keep_unreachable_from", "php_url_parse_ex"
        ],
        "2011-03-27-11efb7295e-f7b7b6aa9e": [
            "-unsound_alloc", "-unsound_const_string", "-unsound_recursion",
            "-unsound_noreturn_function", "-unsound_skip_global_array_init",
            "100", "-top_location", "-max_pre_iter", "2",
            "-keep_unreachable_from", "construction_wrapper"
        ],
        "2011-04-07-d3274b7f20-77ed819430": [
            "-unsound_alloc", "-unsound_const_string", "-unsound_recursion",
            "-unsound_noreturn_function", "-unsound_skip_global_array_init",
            "100", "-top_location", "-max_pre_iter", "2",
            "-keep_unreachable_from", "spl_array_unset_dimension_ex"
        ],
        "2011-10-31-c4eb5f2387-2e5d5e5ac6": [
            "-unsound_alloc",
            "-unsound_const_string",
            "-unsound_recursion",
            "-unsound_noreturn_function",
            "-unsound_skip_global_array_init",
            "100",
            "-top_location",
            "-max_pre_iter",
            "2",
        ],
        "2011-11-08-0ac9b9b0ae-cacf363957": [
            "-unsound_alloc",
            "-unsound_const_string",
            "-unsound_recursion",
            "-unsound_noreturn_function",
            "-unsound_skip_global_array_init",
            "100",
            "-top_location",
            "-max_pre_iter",
            "2",
        ],
        "2011-11-08-c3e56a152c-3598185a74": [
            "-unsound_alloc",
            "-unsound_const_string",
            "-unsound_recursion",
            "-unsound_noreturn_function",
            "-unsound_skip_global_array_init",
            "100",
            "-top_location",
            "-max_pre_iter",
            "2",
        ],
        "2011-11-11-fcbfbea8d2-c1e510aea8": [
            "-unsound_alloc",
            "-unsound_const_string",
            "-unsound_recursion",
            "-unsound_noreturn_function",
            "-unsound_skip_global_array_init",
            "100",
            "-top_location",
            "-max_pre_iter",
            "2",
        ],
        "2011-11-19-eeba0b5681-f330c8ab4e": [
            "-unsound_alloc",
            "-unsound_const_string",
            "-unsound_recursion",
            "-unsound_noreturn_function",
            "-unsound_skip_global_array_init",
            "100",
            "-top_location",
            "-max_pre_iter",
            "2",
        ],
        "2011-12-04-1e6a82a1cf-dfa08dc325": [
            "-unsound_alloc", "-unsound_const_string", "-unsound_recursion",
            "-unsound_noreturn_function", "-unsound_skip_global_array_init",
            "100", "-top_location", "-max_pre_iter", "2",
            "-keep_unreachable_from", "php_filter_validate_email"
        ],
        "2012-03-08-0169020e49-cdc512afb3": [
            "-unsound_alloc",
            "-unsound_const_string",
            "-unsound_recursion",
            "-unsound_noreturn_function",
            "-unsound_skip_global_array_init",
            "100",
            "-top_location",
            "-max_pre_iter",
            "2",
        ],
        "2012-03-12-7aefbf70a8-efc94f3115": [
            "-unsound_alloc",
            "-unsound_const_string",
            "-unsound_recursion",
            "-unsound_noreturn_function",
            "-unsound_skip_global_array_init",
            "100",
            "-top_location",
            "-max_pre_iter",
            "2",
        ]
    }
}
