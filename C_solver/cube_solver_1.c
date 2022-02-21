#include <stdio.h>


//definition from Rubikscube_2x2x2.py
enum FACE_IDX{
    SIDE_IDX_UP     = 0,
    SIDE_IDX_DOWN   = 1,
    SIDE_IDX_FRONT  = 2,
    SIDE_IDX_BACK   = 3,
    SIDE_IDX_LEFT   = 4,
    SIDE_IDX_RIGHT  = 5,
};

enum COLOR_BITMAP{
    COL_IDX_WHITE   = 0,        //0b00000000
    COL_IDX_YELLOW  = 1,        //0b00000001
    COL_IDX_ORANGE  = 2,        //0b00000010
    COL_IDX_RED     = 3,        //0b00000011
    COL_IDX_BLUE    = 4,        //0b00000100
    COL_IDX_GREEN   = 5,        //0b00000101
};

const char cColor[6] = "WYORBG";


//i8
enum CUBE_CMD{
    CMD_U_CW = 0,       
    CMD_R_CW = 1,
    CMD_F_CW = 2,
    CMD_U_CCW = 3,
    CMD_R_CCW = 4,
    CMD_F_CCW = 5,
    CMD_U2 = 6,
    CMD_R2 = 7,
    CMD_F2 = 8,
    CMD_END
};

const char *pszCmd[9] = {
    "U", "R", "F", "U'", "R'", "F'", "U2", "R2", "F2"
};


typedef unsigned char       byte;
typedef unsigned char       u8;
typedef unsigned short      u16;
typedef unsigned int        u32;
typedef unsigned long long  u64;

typedef signed char       i8;
typedef signed short      i16;
typedef signed int        i32;
typedef signed long long  i64;


#define U8_MAX          (0xFF)
#define U16_MAX         (0xFFFF)
#define U32_MAX         (0xFFFFFFFF)
#define U64_MAX         (0xFFFFFFFFFFFFFFFF)


typedef struct {
    u32 face[6];
}
trcube_facemap;


u32 _rcube_rotate_face_ccw(u32 u32face, u8 u8num);
u32 _rcube_rotate_face_cw(u32 u32face, u8 u8num);

void rcube_init(trcube_facemap *ptfacemap);
int rcube_load_input(char *pszArg, trcube_facemap *ptfacemap);

void rcube_print_2d(trcube_facemap *ptfacemap);
void rcube_print_2d_flat(trcube_facemap *ptfacemap);
void rcube_cmd(trcube_facemap *ptfacemap, u8 u8cmd);


int main(int argc, char *argv[] )  
{
    int num = 0;
    int iResult = 0;
   

    if( argc == 2 ) {
        printf("The argument supplied is %s\n", argv[1]);
    }
    else if( argc > 2 ) {
        printf("Too many arguments supplied.\n");
        return(-1);
    }
    else {
        printf("One argument expected.\n");
        //dummy injection of an argument
        //char *pszArg = "WWWW-YYYY-OOOO-RRRR-BBBB-GGGG";
        char *pszArg = "RWWW-YYYY-GGOO-RRBB-BOBO-RGRG";
        argv[1] = pszArg;
        printf("dummy argument injected is %s\n", argv[1]);

    }

    trcube_facemap tSolved_cube;
    trcube_facemap tLoaded_cube;
    
    memset(&tSolved_cube, 0x00, sizeof(tSolved_cube));
    memset(&tLoaded_cube, 0x00, sizeof(tLoaded_cube));

    rcube_init(&tSolved_cube);
    iResult = rcube_load_input(argv[1], &tLoaded_cube);
    if(iResult != 0) 
    {
        printf("Error loading input data");
        return(-1);
    }
    //printf("Solved Cube: \n");
    //rcube_print_2d(&tSolved_cube);
    printf("Loaded Cube: \n");
    rcube_print_2d(&tLoaded_cube);
    rcube_cmd(&tLoaded_cube, CMD_U_CCW);
    rcube_print_2d(&tLoaded_cube);
    rcube_cmd(&tLoaded_cube, CMD_U_CW);
    rcube_print_2d(&tLoaded_cube);

    rcube_cmd(&tLoaded_cube, CMD_U2);
    rcube_print_2d(&tLoaded_cube);

    //rcube_print_2d_flat(&tSolved_cube);
    //rcube_print_2d_flat(&tLoaded_cube);
    

    //printf("0x%016x, 0x%016x, 0x%016x, 0x%016llx, \n", u8max, u16max, u32max, u64max);
    return(0);

}



/* facemap definition   byte-order in u32 (little endian)
[TL] [TR]               [0] [1]
[BL] [BR]               [3] [2]
*/
//get value from u32face
#define TL_GET(val)             (val & 0x000000FF)              //TOP LEFT
#define TR_GET(val)             ((val & 0x0000FF00)>>8)         //TOP RIGHT
#define BR_GET(val)             ((val & 0x00FF0000)>>16)        //BOT RIGHT
#define BL_GET(val)             ((val & 0xFF000000)>>24)        //BOT LEFT

//get character from u32face-value (only debug)
#define TL_GET_CHAR(val)         cColor[TL_GET(val)]
#define TR_GET_CHAR(val)         cColor[TR_GET(val)]
#define BR_GET_CHAR(val)         cColor[BR_GET(val)]
#define BL_GET_CHAR(val)         cColor[BL_GET(val)]

//set value to u32face (clear dest bits and set new val)
#define TL_SET(dest, val)         (dest = (dest&0xFFFFFF00) | (val & 0x000000FF))               //TOP LEFT
#define TR_SET(dest, val)         (dest = (dest&0xFFFF00FF) | ((val << 8)  & 0x0000FF00))       //TOP RIGHT
#define BR_SET(dest, val)         (dest = (dest&0xFF00FFFF) | ((val << 16) & 0x00FF0000))       //BOT RIGHT
#define BL_SET(dest, val)         (dest = (dest&0x00FFFFFF) | ((val << 24) & 0xFF000000))       //BOT LEFT

//init values = solved cube
#define FACE_WHITE_INIT         ((u32)(COL_IDX_WHITE) + (u32)(COL_IDX_WHITE<<8) + (u32)(COL_IDX_WHITE<<16) + (u32)(COL_IDX_WHITE<<24))
#define FACE_YELLOW_INIT        ((u32)(COL_IDX_YELLOW) + (u32)(COL_IDX_YELLOW<<8) + (u32)(COL_IDX_YELLOW<<16) + (u32)(COL_IDX_YELLOW<<24))
#define FACE_ORANGE_INIT        ((u32)(COL_IDX_ORANGE) + (u32)(COL_IDX_ORANGE<<8) + (u32)(COL_IDX_ORANGE<<16) + (u32)(COL_IDX_ORANGE<<24))
#define FACE_RED_INIT           ((u32)(COL_IDX_RED) + (u32)(COL_IDX_RED<<8) + (u32)(COL_IDX_RED<<16) + (u32)(COL_IDX_RED<<24))
#define FACE_BLUE_INIT          ((u32)(COL_IDX_BLUE) + (u32)(COL_IDX_BLUE<<8) + (u32)(COL_IDX_BLUE<<16) + (u32)(COL_IDX_BLUE<<24))
#define FACE_GREEN_INIT         ((u32)(COL_IDX_GREEN) + (u32)(COL_IDX_GREEN<<8) + (u32)(COL_IDX_GREEN<<16) + (u32)(COL_IDX_GREEN<<24))

/** 
 * @brief  init rcube facemap bitboards with data from input argument
 
 * @note   
 * @param  pszArg: input argument, ascii description for facemap "W" = White, Y=Yellow....  mapping 
 * @param  ptfacemap: rcube facemap bitboard
 * @retval None
 */
int rcube_load_input(char *pszArg, trcube_facemap *ptfacemap)
{
    u8 u8len = strlen(pszArg);
    u8 i = 0;
    u8 j = 0;

    if(u8len != 24+5)
    {
        printf("wrong size of input data: %d, expected 29", u8len);
        return(-1);
    }
    
    for(i=0; i<6; i++)
    {
        u32 *pu32face = &ptfacemap->face[i];
        
        printf("Decode Face %d args = ", i);
        for(j=0; j<4; j++)
        {
            u8 u8Color = 0;
            char cArg = *pszArg;
            printf("%c", cArg);
            pszArg++;

            if(cArg == 'W') {u8Color = COL_IDX_WHITE;}
            else if(cArg == 'Y') {u8Color = COL_IDX_YELLOW;}
            else if(cArg == 'O') {u8Color = COL_IDX_ORANGE;}
            else if(cArg == 'R') {u8Color = COL_IDX_RED;}
            else if(cArg == 'B') {u8Color = COL_IDX_BLUE;}
            else if(cArg == 'G') {u8Color = COL_IDX_GREEN;}
            else {u8Color= COL_IDX_WHITE;}

            if(0 == j) { TL_SET(*pu32face, u8Color); }
            if(1 == j) { TR_SET(*pu32face, u8Color); }
            if(2 == j) { BL_SET(*pu32face, u8Color); }
            if(3 == j) { BR_SET(*pu32face, u8Color); }
        }
        //skip "-"
        pszArg++;
        printf("\n");

    }
    return(0);

    
}
/** 
 * @brief  init rcube facemap bitboards with defaults (=solved state)
 * @note   
 * @param  ptfacemap: rcube facemap bitboard
 * @retval None
 */
void rcube_init(trcube_facemap *ptfacemap)
{
    u8 u8Cnt = 0;
    ptfacemap->face[SIDE_IDX_UP] = FACE_WHITE_INIT;
    ptfacemap->face[SIDE_IDX_DOWN] = FACE_YELLOW_INIT;
    ptfacemap->face[SIDE_IDX_FRONT] = FACE_ORANGE_INIT;
    ptfacemap->face[SIDE_IDX_BACK] = FACE_RED_INIT;
    ptfacemap->face[SIDE_IDX_LEFT] = FACE_BLUE_INIT;
    ptfacemap->face[SIDE_IDX_RIGHT] = FACE_GREEN_INIT;
}


/** 
 * @brief  print 2d facemap, traditional style
 *                [back]
 *         [left] [up]    [right]  [down]
 *                [front]
 * @note   
 * @param  ptfacemap: rcube facemap bitboard
 * @retval None
 */
void rcube_print_2d(trcube_facemap *ptfacemap)
{
    u32 u32face_b = ptfacemap->face[SIDE_IDX_BACK];
    u32 u32face_l = ptfacemap->face[SIDE_IDX_LEFT];
    u32 u32face_u = ptfacemap->face[SIDE_IDX_UP];
    u32 u32face_r = ptfacemap->face[SIDE_IDX_RIGHT];
    u32 u32face_d = ptfacemap->face[SIDE_IDX_DOWN];
    u32 u32face_f = ptfacemap->face[SIDE_IDX_FRONT];

    printf("    %c %c\n    %c %c\n", TL_GET_CHAR(u32face_b), TR_GET_CHAR(u32face_b),BL_GET_CHAR(u32face_b),BR_GET_CHAR(u32face_b));
    
    printf("%c %c %c %c %c %c %c %c\n", \
    TL_GET_CHAR(u32face_l), TR_GET_CHAR(u32face_l),\
    TL_GET_CHAR(u32face_u), TR_GET_CHAR(u32face_u),\
    TL_GET_CHAR(u32face_r), TR_GET_CHAR(u32face_r),\
    TL_GET_CHAR(u32face_d), TR_GET_CHAR(u32face_d)\
    );
    printf("%c %c %c %c %c %c %c %c\n", \
    BL_GET_CHAR(u32face_l), BR_GET_CHAR(u32face_l),\
    BL_GET_CHAR(u32face_u), BR_GET_CHAR(u32face_u),\
    BL_GET_CHAR(u32face_r), BR_GET_CHAR(u32face_r),\
    BL_GET_CHAR(u32face_d), BR_GET_CHAR(u32face_d)\
    );

    printf("    %c %c\n    %c %c\n", TL_GET_CHAR(u32face_f), TR_GET_CHAR(u32face_f),BL_GET_CHAR(u32face_f),BR_GET_CHAR(u32face_f));  

}

/** 
 * @brief  print compact 2d facemap (flat) - 2 console lines [up][down][front][back][left][right]
 * @note   
 * @param  ptfacemap: rcube facemap bitboard
 * @retval None
 */
void rcube_print_2d_flat(trcube_facemap *ptfacemap)
{
    u32 *pu32face = ptfacemap->face;
    printf("%c %c %c %c %c %c %c %c %c %c %c %c\n\r", \
    TL_GET_CHAR(pu32face[0]), TR_GET_CHAR(pu32face[0]),\
    TL_GET_CHAR(pu32face[1]), TR_GET_CHAR(pu32face[1]),\
    TL_GET_CHAR(pu32face[2]), TR_GET_CHAR(pu32face[2]),\
    TL_GET_CHAR(pu32face[3]), TR_GET_CHAR(pu32face[3]),\
    TL_GET_CHAR(pu32face[4]), TR_GET_CHAR(pu32face[4]),\
    TL_GET_CHAR(pu32face[5]), TR_GET_CHAR(pu32face[5])\
    );
    
    printf("%c %c %c %c %c %c %c %c %c %c %c %c\n\r", \
    BL_GET_CHAR(pu32face[0]), BR_GET_CHAR(pu32face[0]),\
    BL_GET_CHAR(pu32face[1]), BR_GET_CHAR(pu32face[1]),\
    BL_GET_CHAR(pu32face[2]), BR_GET_CHAR(pu32face[2]),\
    BL_GET_CHAR(pu32face[3]), BR_GET_CHAR(pu32face[3]),\
    BL_GET_CHAR(pu32face[4]), BR_GET_CHAR(pu32face[4]),\
    BL_GET_CHAR(pu32face[5]), BR_GET_CHAR(pu32face[5])\
    );

};

/** 
 * @brief  execute action on rcube (U, U2, U', R, R2, R', F, F2, F')
 * @note   
 * @param  u32face: rcube facemap bitboard
 * @retval None
 */
void rcube_cmd(trcube_facemap *ptfacemap, u8 u8cmd)
{
    switch(u8cmd)
    {
        case CMD_U_CW:
        {
            ptfacemap->face[SIDE_IDX_UP] = _rcube_rotate_face_cw(ptfacemap->face[SIDE_IDX_UP], 1);
            break;
        }      
        case CMD_U_CCW:
        {
            ptfacemap->face[SIDE_IDX_UP] = _rcube_rotate_face_ccw(ptfacemap->face[SIDE_IDX_UP], 1);
            break;
        }      
        case CMD_U2:
        {
            ptfacemap->face[SIDE_IDX_UP] = _rcube_rotate_face_cw(ptfacemap->face[SIDE_IDX_UP], 2);
            break;
        }      


        default:
        {
            printf("rcube_cmd(): Invalid command \n");
            return;
        }
    }
}

/** 
 * @brief  rotate array function (bitwise shifting), used on u32face (primary face)
 * @note   
 * @param  u32face: primary face
 * @param  u32num: number of rotates (1 = 90°, 2=...)
 * @retval None
 */
u32 _rcube_rotate_face_ccw(u32 u32face, u8 u8num)
{
    u8num <<= 3;        //*8
    return((u32face >> u8num)|((u32face << (32-u8num))));
}

u32 _rcube_rotate_face_cw(u32 u32face, u8 u8num)
{
    u8num <<= 3;        //*8
    return((u32face << u8num)|((u32face >> (32-u8num))));
}
