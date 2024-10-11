/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global Office */

Office.onReady(() => {
  // If needed, Office.js is ready to be called.
}); 

/**
 * Opens a new event window when the add-in command is executed.
 * @param event {Office.AddinCommands.Event}
 */
function action(event) {
  Office.onReady((info) => {
    if (info.host === Office.HostType.Outlook) {
      console.log(`Current user: ${Office.context.mailbox.userProfile.emailAddress}`);
      Office.context.mailbox.displayNewAppointmentForm({
        requiredAttendees: ['qwer@cmsinvest.com.br'], //cliente
        optionalAttendees: ['optional1@example.com'], //investor e assistente
        subject: Office.context.mailbox.userProfile.emailAddress,
        location: 'Meeting Room 1',
        body: 'Agenda of the meeting.',
        start: new Date(new Date()),  
        end: new Date(new Date())     
      });
    }
  });
  event.completed();
}


// Register the function with Office.
Office.actions.associate("action", action);
