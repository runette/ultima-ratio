import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import {BcpHomeComponent} from './bcp-home/bcp-home.component';
import {BcpDatabaseComponent} from './bcp-database/bcp-database.component';
import {BcpNewRecordComponent} from './bcp-new-record/bcp-new-record.component';
import {BcpRecordDetailComponent} from './bcp-record-detail/bcp-record-detail.component';
import {BcpHelpComponent} from './bcp-help/bcp-help.component';
import {BcpLoginComponent} from './bcp-login/bcp-login.component';


const routes: Routes = [
{ path: '', component: BcpHomeComponent },
{ path: 'database', component: BcpDatabaseComponent },
{ path: 'new_record', component: BcpNewRecordComponent},
{ path: 'database/entry', component: BcpRecordDetailComponent},
{ path: 'recording', component: BcpHelpComponent},
{ path: 'login', component: BcpLoginComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }