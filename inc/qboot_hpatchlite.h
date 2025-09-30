/**
 * @file qboot_hpatchlite.h
 * @brief 
 * @author huangly ()
 * @version 1.0
 * @date 2025-09-25
 * 
 * @copyright Copyright (c) 2025  
 * 
 * @note :
 * @par 修改日志:
 * Date       Version Author      Description
 * 2025-09-25 1.0     huangly     first version
 */
#ifndef __QBOOT_HPATCHLITE_H__
#define __QBOOT_HPATCHLITE_H__

#include <stdbool.h>
#include <fal.h>
#include "qboot.h"

#ifdef QBOOT_USING_HPATCHLITE
int qbt_hpatchlite_release_from_part(const fal_partition_t patch_part,const fal_partition_t old_part, int patch_file_len, int newer_file_len, int patch_file_offset);
#endif // QBOOT_USING_HPATCHLITE

#endif  //__QBOOT_HPATCHLITE_H__
