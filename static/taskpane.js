/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global document, Office */

Office.onReady(function(info) {
  if (info.host === Office.HostType.Outlook) {
      const userEmail = Office.context.mailbox.userProfile.emailAddress;
      console.log("User Email:", userEmail);
  }
});


/**
 * Opens a new event window when the add-in command is executed.
 * @param event {Office.AddinCommands.Event}
 */



document.addEventListener("DOMContentLoaded", function () {
  
  Office.onReady(function (info) {
      if (info.host === Office.HostType.Outlook) {
          //
          const userEmail = Office.context.mailbox.userProfile.emailAddress;
          const form = document.getElementById("client-form");
          const submitButton = document.getElementById("submit-button");

          form.addEventListener("submit", function (event) {
              event.preventDefault();
              const clientCode = document.getElementById("client-code").value;
              const data = {
                  client_code: clientCode,
                  userEmail: userEmail 
              };

              fetch('/submit-client-code', {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                  },
                  body: JSON.stringify(data),
              })
              .then(response => response.json())
              .then(data => {
                  console.log('Success:', data);
                  document.getElementById("client-code").value = '';
              })
              .catch((error) => {
                  console.error('Error:', error);
              });
          });
      }
  });
});
