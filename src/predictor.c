//========================================================//
//  predictor.c                                           //
//  Source file for the Branch Predictor                  //
//                                                        //
//  Implement the various branch predictors below as      //
//  described in the README                               //
//========================================================//
#include <stdio.h>
#include "predictor.h"
// #include "tournament.h"

//
// TODO:Student Information
//
const char *studentName = "Jiayi Hu";
const char *studentID = "A59012494";
const char *email = "jih071@ucsd.edu";

//------------------------------------//
//      Predictor Configuration       //
//------------------------------------//

// Handy Global for use in output routines
const char *bpName[4] = {"Static", "Gshare",
                         "Tournament", "Custom"};

int ghistoryBits; // Number of bits used for Global History
int lhistoryBits; // Number of bits used for Local History
int pcIndexBits;  // Number of bits used for PC index
int bpType;       // Branch Prediction Type
int verbose;

//------------------------------------//
//      Predictor Data Structures     //
//------------------------------------//
uint8_t *pht; // gshare
uint8_t ghist;

uint32_t gmask;
uint32_t lmask;
uint32_t pcmask;

uint32_t *ht_local;
uint8_t *pht_local;
uint8_t *pht_global;
uint8_t *choices;

// TNM_Predictor *tnm;
//
// TODO: Add your own Branch Predictor data structures here
//
void init_gshare()
{
  pht = (uint8_t *)malloc(sizeof(uint8_t) * (1 << ghistoryBits));
  ghist = 0;
  for (int i = 0; i < (1 << ghistoryBits); i++)
    *(pht + i) = WN;
}

void init_tournament()
{
  ht_local = (uint32_t *)malloc(sizeof(uint32_t) * (1 << pcIndexBits));
  for (int i = 0; i < (1 << pcIndexBits); i++)
    ht_local[i] = 0;

  pht_local = (uint8_t *)malloc(sizeof(uint8_t) * (1 << lhistoryBits));
  for (int i = 0; i < (1 << lhistoryBits); i++)
    pht_local[i] = WN;

  pht_global = (uint8_t *)malloc(sizeof(uint8_t) * (1 << ghistoryBits));
  for (int i = 0; i < (1 << ghistoryBits); i++)
    pht_global[i] = WN;

  choices = (uint8_t *)malloc(sizeof(uint8_t) * (1 << ghistoryBits));
  for (int i = 0; i < (1 << ghistoryBits); i++)
    choices[i] = 1;

  pcmask = (1 << pcIndexBits) - 1;
  lmask = (1 << lhistoryBits) - 1;
  gmask = (1 << ghistoryBits) - 1;
}

uint8_t predict_gshare(uint32_t pc)
{
  int idx = (pc ^ ghist) & ((1 << ghistoryBits) - 1);
  uint8_t decision = *(pht + idx);
  if (decision == WT || decision == ST)
    return TAKEN;
  else
    return NOTTAKEN;
}

uint8_t predict_tournament(uint32_t pc)
{
  uint8_t local_idx = ht_local[pc & pcmask];
  uint8_t declocal = pht_local[local_idx];
  uint8_t global_idx = (pc ^ ghist) & gmask;
  uint8_t decglobal = pht_global[local_idx];
  if (choices[global_idx] == 1)
  {
    if (decglobal == WT || decglobal == ST)
      return TAKEN;
    else
      return NOTTAKEN;
  }
  else
  {
    if (declocal == WT || declocal == ST)
      return TAKEN;
    else
      return NOTTAKEN;
  }
}

void tournament_train(uint32_t pc, uint8_t outcome)
{
  uint8_t local_idx = ht_local[pc & pcmask];
  uint8_t declocal = pht_local[local_idx];
  uint8_t global_idx = (pc ^ ghist) & gmask;
  uint8_t decglobal = pht_global[local_idx];
  if (decglobal == WT || decglobal == ST)
    decglobal = TAKEN;
  else
    decglobal = NOTTAKEN;

  if (declocal == WT || declocal == ST)
    declocal = TAKEN;
  else
    declocal = NOTTAKEN;

  if (outcome && declocal != ST)
    pht_local[local_idx]++;
  else if (!outcome && declocal != SN)
    pht_local[local_idx]--;

  if (outcome && decglobal != ST)
    pht_global[global_idx]++;
  else if (!outcome && decglobal != SN)
    pht_global[global_idx]--;

  if (outcome == decglobal && outcome != declocal)
    choices[global_idx] = 1;
  else if (outcome == declocal && outcome != decglobal)
    choices[global_idx] = 0;

  ghist = (ghist << 1) | outcome & gmask;
  ht_local[pc & pcmask] = (ht_local[pc & pcmask] << 1) | outcome & lmask;
}

void gshare_train(uint32_t pc, uint8_t outcome)
{
  int idx = (pc ^ ghist) & ((1 << ghistoryBits) - 1);
  
  uint8_t decision = *(pht + idx);
  if (outcome && decision != ST)
  {
    *(pht + idx) = decision + 1;
  }
  else if (!outcome && decision != SN)
  {
    *(pht + idx) = decision - 1;
  }
  ghist = (outcome | (ghist << 1)) & ((1 << ghistoryBits) - 1);
}

//------------------------------------//
//        Predictor Functions         //
//------------------------------------//

// Initialize the predictor
//
void init_predictor()
{
  //
  // TODO: Initialize Branch Predictor Data Structures
  //
  switch (bpType)
  {
  case STATIC:
  case GSHARE:
    init_gshare();
    break;
  case TOURNAMENT:
    init_tournament();
    break;
  case CUSTOM:
  default:
    break;
  }
}

// Make a prediction for conditional branch instruction at PC 'pc'
// Returning TAKEN indicates a prediction of taken; returning NOTTAKEN
// indicates a prediction of not taken
//
uint8_t
make_prediction(uint32_t pc)
{
  //
  // TODO: Implement prediction scheme
  //

  // Make a prediction based on the bpType
  switch (bpType)
  {
  case STATIC:
    return TAKEN;
  case GSHARE:
    return predict_gshare(pc);
  case TOURNAMENT:
    return predict_tournament(pc);
  case CUSTOM:
  default:
    break;
  }

  // If there is not a compatable bpType then return NOTTAKEN
  return NOTTAKEN;
}

// Train the predictor the last executed branch at PC 'pc' and with
// outcome 'outcome' (true indicates that the branch was taken, false
// indicates that the branch was not taken)
//
void train_predictor(uint32_t pc, uint8_t outcome)
{
  //
  // TODO: Implement Predictor training
  //
  switch (bpType)
  {
  case STATIC:
  case GSHARE:
    gshare_train(pc, outcome);
    break;
  case TOURNAMENT:
    tournament_train(pc, outcome);
    break;
  case CUSTOM:
  default:
    break;
  }
}
