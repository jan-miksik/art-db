const { Auth, Akord } = require("@akord/akord-js");
const fs = require('fs');
const path = require('path');

const VAULT_ID = '8b513cd6-4136-4150-90fb-9190d9a7034a'
const EMAIL = "miksik.jan@proton.me"; 
const PASSWORD = "TrochuDelsiP@ssw0rd";

const uploadFile = async(filePath) => {
  const { wallet } = await Auth.signIn(EMAIL, PASSWORD);
  const akord = await Akord.init(wallet);
  
  const { stackId, uri } = await akord.stack.create(VAULT_ID, filePath);
  return { stackId, uri };
}

